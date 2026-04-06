import { postJson } from "../core/api.js";
import { updateCartBadge } from "../ui/cartBadge.js";

export async function updateCart(productId, action, csrfToken) {
    try {
        const data = await postJson(
            "/store/update_item/",
            { bookId: productId, action },
            csrfToken
        );

        console.log("Server response:", data);

        updateCartBadge(data.cartItems);

        if (window.location.pathname.includes("/cart")) {
            window.location.reload();
        }

        return data;
    } catch (error) {
        console.error("Cart error:", error);
        return null;
    }
}
