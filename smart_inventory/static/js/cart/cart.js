import { postJson } from "../core/api.js";
import { updateCartBadge } from "../ui/cartBadge.js";
import { showModalMessage } from "../ui/modal.js";

export async function updateCart(productId, action, csrfToken, button = null) {
    if (!productId || !action) {
        showModalMessage("Невалиден продукт или действие.", "error");
        return null;
    }

    try {
        if (button) {
            button.disabled = true;
            button.classList.add("disabled");
        }

        const data = await postJson(
            "/store/update_item/",
            { bookId: productId, action },
            csrfToken
        );

        updateCartBadge(data.cartItems);

        if (window.location.pathname.includes("/cart")) {
            window.location.reload();
        }

        return data;
    } catch (error) {
        showModalMessage(error.message || "Грешка при обновяване на количката.", "error");
        return null;
    } finally {
        if (button) {
            button.disabled = false;
            button.classList.remove("disabled");
        }
    }
}
