import { postJson } from "../core/api.js";
import { updateCartBadge } from "../ui/cartBadge.js";

export async function updateCart(productId, action, csrfToken) {
    try {
        const data = await postJson(
            "/store/update_item/",
            { bookId: productId, action },
            csrfToken
        );
        updateCartBadge(data.cartItems);
    } catch (error) {
        console.error("Cart error:", error);
    }
}
