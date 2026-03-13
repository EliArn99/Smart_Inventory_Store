import {postJson} from "../core/api.js";
import {updateCartBadge} from "../ui/cartBadge.js";

export async function updateCart(productId, action, csrfToken) {

    const data = await postJson(
        "/store/update_item/",
        {bookId: productId, action},
        csrfToken
    );

    updateCartBadge(data.cartItems);
}
