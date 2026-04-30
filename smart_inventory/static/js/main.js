import { getCookie } from "./core/cookies.js";
import { ensureMessageModal } from "./ui/modal.js";
import { initCheckout } from "./cart/checkout.js";
import { updateCart } from "./cart/cart.js";
import { updateWishlist } from "./cart/wishlist.js";

document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = getCookie("csrftoken");

    ensureMessageModal();
    initCheckout(csrfToken);

    document.addEventListener("click", async (event) => {
        const cartBtn = event.target.closest(".update-cart");

        if (cartBtn) {
            event.preventDefault();

            const productId = cartBtn.dataset.product;
            const action = cartBtn.dataset.action;

            await updateCart(productId, action, csrfToken, cartBtn);
            return;
        }

        const wishlistBtn = event.target.closest(".update-wishlist");

        if (wishlistBtn) {
            event.preventDefault();

            const bookId = wishlistBtn.dataset.book;
            const action = wishlistBtn.dataset.action;

            await updateWishlist(bookId, action, csrfToken, wishlistBtn);
        }
    });
});
