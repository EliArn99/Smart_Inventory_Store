import { postJson } from "../core/api.js";
import { showModalMessage } from "../ui/modal.js";

export async function updateWishlist(bookId, action, csrfToken, button = null) {
    if (!bookId || !action) {
        showModalMessage("Невалиден продукт или действие.", "error");
        return null;
    }

    try {
        if (button) {
            button.disabled = true;
            button.classList.add("disabled");
        }

        const data = await postJson(
            "/store/update_wishlist/",
            { bookId, action },
            csrfToken
        );

        if (data.message) {
            showModalMessage(data.message, "success");
        }

        if (button && typeof data.added !== "undefined") {
            button.dataset.action = data.added ? "remove" : "add";
        }

        return data;
    } catch (error) {
        showModalMessage(error.message || "Грешка при обновяване на любими.", "error");
        return null;
    } finally {
        if (button) {
            button.disabled = false;
            button.classList.remove("disabled");
        }
    }
}
