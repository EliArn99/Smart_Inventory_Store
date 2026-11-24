
import { postJson } from "../core/api.js";
import { showModalMessage } from "../ui/modal.js";

const CHECKOUT_KEY_STORAGE = "stockpilot_checkout_key";

export function initCheckout(csrfToken) {
    const form = document.getElementById("form");
    if (!form) return;

    let isSubmitting = false;
    let checkoutCompleted = false;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Prevent multiple submissions from the same page.
        if (isSubmitting || checkoutCompleted) {
            return;
        }

        isSubmitting = true;

        const submitButton = form.querySelector(
            'button[type="submit"], input[type="submit"]'
        );

        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            // Reuse the key if the previous request needs a retry.
            let idempotencyKey = sessionStorage.getItem(
                CHECKOUT_KEY_STORAGE
            );

            if (!idempotencyKey) {
                idempotencyKey = crypto.randomUUID();

                sessionStorage.setItem(
                    CHECKOUT_KEY_STORAGE,
                    idempotencyKey
                );
            }

            const total = (
                document.getElementById("order-total")
                    ?.textContent.trim() || "0"
            );

            const payload = {
                idempotency_key: idempotencyKey,
                form: {
                    name: form.name.value,
                    email: form.email.value,
                    total: total
                },
                shipping: {
                    address: form.address.value,
                    city: form.city.value,
                    zipcode: form.zipcode.value
                }
            };

            await postJson(
                "/store/process_order/",
                payload,
                csrfToken
            );

            checkoutCompleted = true;

            // Remove the key only after confirmed success.
            sessionStorage.removeItem(CHECKOUT_KEY_STORAGE);

            showModalMessage(
                "Поръчката е завършена!",
                "success"
            );

            document.cookie =
                "cart=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

            setTimeout(() => {
                window.location.href = "/store/";
            }, 2000);

        } catch (error) {
            // Keep the key for retry after an error.
            showModalMessage(error.message, "error");

        } finally {
            isSubmitting = false;

            if (submitButton && !checkoutCompleted) {
                submitButton.disabled = false;
            }
        }
    });
}
