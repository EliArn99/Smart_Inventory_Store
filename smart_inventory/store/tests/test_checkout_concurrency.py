
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections, connections
from django.test import (
    RequestFactory,
    TransactionTestCase,
    skipUnlessDBFeature,
)

from store.models import Order, Product
from store.views import process_order


@skipUnlessDBFeature("has_select_for_update")
class CheckoutIdempotencyConcurrencyTests(TransactionTestCase):
    def test_concurrent_requests_with_same_key_create_one_order(self):
        product = Product.objects.create(
            name="Concurrent Checkout Product",
            price=Decimal("20.00"),
            stock=2,
            digital=True,
        )

        checkout_key = str(uuid.uuid4())
        barrier = Barrier(2)

        def submit_checkout():
            close_old_connections()

            try:
                request = RequestFactory().post(
                    "/store/process_order/",
                    data={
                        "idempotency_key": checkout_key,
                        "form": {
                            "name": "Concurrent Guest",
                            "email": "concurrent-checkout@example.com",
                        },
                    },
                    content_type="application/json",
                )

                request.user = AnonymousUser()
                request.COOKIES["cart"] = json.dumps(
                    {str(product.pk): {"quantity": 1}}
                )

                barrier.wait(timeout=15)

                return process_order(request).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(submit_checkout)
                for _ in range(2)
            ]

            statuses = [
                future.result(timeout=30)
                for future in futures
            ]

        product.refresh_from_db()

        orders = Order.objects.filter(
            customer__email="concurrent-checkout@example.com"
        )

        self.assertEqual(sorted(statuses), [200, 200])
        self.assertEqual(orders.count(), 1)
        self.assertTrue(orders.get().complete)
        self.assertEqual(product.stock, 1)
