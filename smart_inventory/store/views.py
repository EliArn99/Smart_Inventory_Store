import json
import logging
import uuid

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from .forms import CommentForm, CustomUserCreationForm, PostForm, ReviewForm
from .models import (
    Banner,
    BlogCategory,
    Book,
    Category,
    Customer,
    Order,
    OrderItem,
    Post,
    Review,
    ShippingAddress,
    WishlistItem,
)
from .utils import cartData, cookieCart, guestOrder

logger = logging.getLogger(__name__)


def get_or_create_customer_for_user(user):
    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": getattr(user, "username", "") or "",
            "email": getattr(user, "email", "") or "",
        },
    )
    return customer


class BaseContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = cartData(self.request)
        context["cartItems"] = data["cartItems"]
        return context


class CartMixin(BaseContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = cartData(self.request)
        context["order"] = data["order"]
        context["items"] = data["items"]
        return context


class BookListView(BaseContextMixin, ListView):
    model = Book
    template_name = "store/store.html"
    context_object_name = "books_on_page"
    paginate_by = 12

    def get_queryset(self):
        books = (
            Book.objects.select_related("category")
            .annotate(avg_rating=Avg("reviews__rating"))
            .annotate(reviews_count=Count("reviews"))
        )

        query = self.request.GET.get("q")
        if query:
            books = books.filter(
                Q(name__icontains=query)
                | Q(author__icontains=query)
                | Q(description__icontains=query)
            ).distinct()

        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            books = books.filter(category__slug=category_slug)

        author = self.request.GET.get("author")
        if author:
            books = books.filter(author__icontains=author)

        year = self.request.GET.get("year")
        if year:
            try:
                books = books.filter(publication_year=int(year))
            except (TypeError, ValueError):
                pass

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            books = books.filter(price__gte=min_price)
        if max_price:
            books = books.filter(price__lte=max_price)

        sort_by = self.request.GET.get("sort_by", "name")
        order = self.request.GET.get("order", "asc")

        valid_sort_fields = ["name", "price", "avg_rating", "publication_year"]
        if sort_by in valid_sort_fields:
            if order == "desc":
                books = books.order_by(F(sort_by).desc(nulls_last=True))
            else:
                books = books.order_by(F(sort_by).asc(nulls_last=True))
        else:
            books = books.order_by("name")

        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(book_count=Count("book"))
        context["banners"] = Banner.objects.filter(is_active=True).order_by("order")
        context["active_category_slug"] = self.kwargs.get("category_slug")
        context["query"] = self.request.GET.get("q")
        context["min_price"] = self.request.GET.get("min_price")
        context["max_price"] = self.request.GET.get("max_price")
        context["author"] = self.request.GET.get("author")
        context["year"] = self.request.GET.get("year")
        context["sort_by"] = self.request.GET.get("sort_by", "name")
        context["order"] = self.request.GET.get("order", "asc")
        return context


class AboutUsView(BaseContextMixin, TemplateView):
    template_name = "store/about_us.html"


class CartView(CartMixin, TemplateView):
    template_name = "store/cart.html"


class CheckoutView(CartMixin, TemplateView):
    template_name = "store/checkout.html"


@require_POST
def update_item(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Невалиден JSON."}, status=400)

    book_id = data.get("bookId")
    action = data.get("action")

    if not book_id or action not in {"add", "remove"}:
        return JsonResponse({"error": "Невалидни входни данни."}, status=400)

    book = get_object_or_404(Book, pk=book_id)

    if request.user.is_authenticated:
        customer = get_or_create_customer_for_user(request.user)
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        order_item, _ = OrderItem.objects.get_or_create(order=order, product=book)

        if action == "add":
            order_item.quantity = (order_item.quantity or 0) + 1
            order_item.save()
        else:
            order_item.quantity = (order_item.quantity or 0) - 1
            if order_item.quantity <= 0:
                order_item.delete()
            else:
                order_item.save()

        return JsonResponse({"cartItems": order.get_cart_items})

    cookie_data = cookieCart(request)
    cart = cookie_data.get("cart", {})
    book_key = str(book_id)

    if action == "add":
        quantity = cart.get(book_key, {"quantity": 0}).get("quantity", 0) + 1
        cart[book_key] = {"quantity": quantity}
    else:
        if book_key in cart:
            cart[book_key]["quantity"] -= 1
            if cart[book_key]["quantity"] <= 0:
                del cart[book_key]

    cart_items_count = sum(item.get("quantity", 0) for item in cart.values())
    response = JsonResponse({"cartItems": cart_items_count})
    response.set_cookie("cart", json.dumps(cart))
    return response


@require_POST
def process_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Невалиден JSON."}, status=400)

    try:
        if request.user.is_authenticated:
            customer = get_or_create_customer_for_user(request.user)
            order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        with transaction.atomic():
            order.transaction_id = uuid.uuid4().hex

            items = order.orderitem_set.select_related("product").select_for_update()

            for item in items:
                book = item.product
                if book is None:
                    return JsonResponse({"error": "Невалиден продукт в поръчката."}, status=400)

                if book.stock < item.quantity:
                    return JsonResponse(
                        {"error": f'Недостатъчна наличност за книга "{book.name}".'},
                        status=400,
                    )

            for item in items:
                Book.objects.filter(pk=item.product_id).update(stock=F("stock") - item.quantity)

            order.complete = True
            order.save(update_fields=["transaction_id", "complete"])

            if order.shipping:
                shipping = data.get("shipping", {})
                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=shipping.get("address", ""),
                    city=shipping.get("city", ""),
                    state=shipping.get("state", ""),
                    zipcode=shipping.get("zipcode", ""),
                )

        response = JsonResponse({"message": "Payment submitted successfully"}, status=200)

        if not request.user.is_authenticated:
            response.delete_cookie("cart")

        return response

    except Exception:
        logger.exception("Грешка при обработка на поръчка.")
        return JsonResponse({"error": "Възникна грешка при обработка на поръчката."}, status=500)


def get_cart_data(request):
    data = cartData(request)
    data["order"]["get_cart_total"] = float(data["order"]["get_cart_total"])

    for item in data["items"]:
        item["product"]["price"] = float(item["product"]["price"])
        item["get_total"] = float(item["get_total"])

    return JsonResponse(data, safe=False)


@login_required
def profile_details(request):
    customer = get_or_create_customer_for_user(request.user)
    orders = customer.order_set.all().order_by("-date_ordered")

    purchased_categories = Category.objects.filter(
        book__orderitem__order__customer=customer
    ).distinct()

    recommended_books = (
        Book.objects.filter(category__in=purchased_categories)
        .exclude(orderitem__order__customer=customer)
        .distinct()
        .order_by("?")
    )

    if not recommended_books.exists():
        recommended_books = Book.objects.all().order_by("?")[:4]
    else:
        recommended_books = recommended_books[:4]

    context = {
        "customer": customer,
        "orders": orders,
        "recommended_books": recommended_books,
    }
    return render(request, "store/profile_details.html", context)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрацията беше успешна.")
            return redirect("store:store")

        messages.error(request, "Моля, поправете грешките във формата.")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


class BookDetailView(BaseContextMixin, DetailView, FormView):
    model = Book
    template_name = "store/book_detail.html"
    context_object_name = "book"
    pk_url_kwarg = "pk"
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.reviews.all().order_by("-created_at")
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Трябва да сте влезли, за да оставите ревю.")
            return redirect("login")

        self.object = self.get_object()

        if Review.objects.filter(book=self.object, user=request.user).exists():
            messages.warning(request, "Вече сте оставили ревю за тази книга.")
            return redirect("store:book_detail", pk=self.object.pk)

        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.book = self.object
            review.user = request.user
            review.save()
            messages.success(request, "Вашето ревю беше успешно добавено!")
            return redirect("store:book_detail", pk=self.object.pk)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


@login_required
@require_POST
def update_wishlist(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Невалиден JSON."}, status=400)

    book_id = data.get("bookId")
    action = data.get("action")

    if not book_id or action not in {"add", "remove"}:
        return JsonResponse({"error": "Missing or invalid bookId/action."}, status=400)

    book = get_object_or_404(Book, id=book_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

    if action == "add":
        message = (
            "Книгата е добавена в списъка с желания."
            if created
            else "Книгата вече е в списъка с желания."
        )
        added = True
    else:
        if created:
            message = "Книгата не е в списъка с желания."
            added = False
        else:
            wishlist_item.delete()
            message = "Книгата е премахната от списъка с желания."
            added = False

    return JsonResponse({"message": message, "added": added, "book_id": book_id})


@login_required(login_url="login")
def wishlist_view(request):
    user_wishlist = WishlistItem.objects.filter(user=request.user).select_related("book")
    data = cartData(request)

    context = {
        "wishlist_items": user_wishlist,
        "cartItems": data["cartItems"],
    }
    return render(request, "store/wishlist.html", context)


class BlogListView(BaseContextMixin, ListView):
    model = Post
    template_name = "store/blog_list.html"
    context_object_name = "posts_list"
    paginate_by = 6
    queryset = (
        Post.objects.filter(status=1)
        .select_related("category", "author")
        .order_by("-created_on")
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BlogCategory.objects.all()
        return context


class PostsByCategoryView(BlogListView):
    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        self.category = get_object_or_404(BlogCategory, slug=category_slug)
        return (
            Post.objects.filter(category=self.category, status=1)
            .select_related("category", "author")
            .order_by("-created_on")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_category"] = self.category
        return context


class BlogDetailView(BaseContextMixin, DetailView, FormView):
    model = Post
    template_name = "store/blog_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(Post, slug=self.kwargs.get("slug"), status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.filter(is_approved=True).order_by("-created_on")
        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Трябва да сте влезли, за да коментирате.")
            return redirect("login")

        new_comment = form.save(commit=False)
        new_comment.post = self.get_object()
        new_comment.user = self.request.user
        new_comment.save()

        messages.success(self.request, "Вашият коментар е изпратен и очаква одобрение.")
        return redirect("store:blog_detail", slug=self.kwargs.get("slug"))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


@staff_member_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Публикацията беше успешно създадена!")
            return redirect("store:blog_list")
    else:
        form = PostForm()

    return render(request, "store/add_post.html", {"form": form})


@staff_member_required
def inventory_report_view(request):
    low_stock_books = Book.objects.filter(stock__lte=5).order_by("stock")

    context = {
        "low_stock_books": low_stock_books,
    }
    return render(request, "admin/inventory_report.html", context)


@login_required
def order_detail(request, order_id):
    customer = get_or_create_customer_for_user(request.user)
    order = get_object_or_404(Order, id=order_id)

    if order.customer != customer:
        raise Http404("You don't have permission to view this order.")

    context = {
        "order": order,
        "order_items": order.orderitem_set.select_related("product").all(),
    }
    return render(request, "store/order_detail.html", context)


# Backward-compatible aliases if your urls.py still points to the old names.
updateItem = update_item
processOrder = process_order
