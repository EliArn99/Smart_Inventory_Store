import { postJson } from "../core/api.js";
import { showModalMessage } from "../ui/modal.js";

export function initCheckout(csrfToken) {
    const form = document.getElementById("form");

    if (!form) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        toggleCheckoutLoading(true);

        try {
            await submitOrder(form, csrfToken);

            showModalMessage("Поръчката беше успешно завършена!", "success");

            clearCartCookie();

            setTimeout(() => {
                window.location.href = "/store/store/";
            }, 3000);
        } catch (error) {
            console.error("Грешка при обработка на поръчката:", error);

            showModalMessage(
                error.message || "Възникна грешка при обработка на поръчката.",
                "error"
            );

            toggleCheckoutLoading(false);
        }
    });
}

function toggleCheckoutLoading(isLoading) {
    const formButton = document.getElementById("form-button");
    const loadingSpinner = document.getElementById("loading-spinner");

    if (formButton) {
        formButton.classList.toggle("d-none", isLoading);
    }

    if (loadingSpinner) {
        loadingSpinner.classList.toggle("d-none", !isLoading);
    }
}

async function submitOrder(form, csrfToken) {
    const totalElement = document.getElementById("order-total");
    const total = totalElement ? totalElement.textContent.trim() : "0";

    const userFormData = {
        name: form.name ? form.name.value.trim() : "",
        email: form.email ? form.email.value.trim() : "",
        total: total,
    };

    const shippingInfo = {
        address: form.address ? form.address.value.trim() : "",
        city: form.city ? form.city.value.trim() : "",
        state: form.state ? form.state.value.trim() : "",
        zipcode: form.zipcode ? form.zipcode.value.trim() : "",
    };

    return await postJson(
        "/store/process_order/",
        {
            form: userFormData,
            shipping: shippingInfo,
        },
        csrfToken
    );
}

function clearCartCookie() {
    document.cookie = "cart=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}
