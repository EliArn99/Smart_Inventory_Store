import { postJson } from "../core/api.js";
import { showModalMessage } from "../ui/modal.js";

export function initCheckout(csrfToken) {
    const form = document.getElementById("form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const total = document.getElementById("order-total")?.textContent.trim() || "0";
            const payload = {
                form: { name: form.name.value, email: form.email.value, total: total },
                shipping: { address: form.address.value, city: form.city.value, zipcode: form.zipcode.value }
            };

            await postJson("/store/process_order/", payload, csrfToken);
            showModalMessage("Поръчката е завършена!", "success");
            document.cookie = "cart=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            setTimeout(() => { window.location.href = "/store/"; }, 2000);
        } catch (error) {
            showModalMessage(error.message, "error");
        }
    });
}
