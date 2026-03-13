import {postJson} from "../core/api.js";

export async function updateWishlist(bookId, action, csrfToken) {

    return await postJson(
        "/store/update_wishlist/",
        {bookId, action},
        csrfToken
    );
}
