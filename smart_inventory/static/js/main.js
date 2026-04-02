import { getCookie } from "./core/cookies.js";
import { ensureMessageModal } from "./ui/modal.js";
import { initCheckout } from "./cart/checkout.js";
import { updateCart } from "./cart/cart.js";
import { updateWishlist } from "./cart/wishlist.js";

console.log("main.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOMContentLoaded from main.js");

    const csrfToken = getCookie("csrftoken");
    console.log("csrfToken:", csrfToken);

    ensureMessageModal();
    initCheckout(csrfToken);

    document.addEventListener("click", (e) => {
        console.log("document click", e.target);

        const cartBtn = e.target.closest(".update-cart");
        if (cartBtn) {
            console.log("cart button clicked");
            const productId = cartBtn.dataset.product;
            const action = cartBtn.dataset.action;
            console.log({ productId, action });
            updateCart(productId, action, csrfToken);
        }

        const wishlistBtn = e.target.closest(".update-wishlist");
        if (wishlistBtn) {
            console.log("wishlist button clicked");
            const bookId = wishlistBtn.dataset.book;
            const action = wishlistBtn.dataset.action;
            updateWishlist(bookId, action, csrfToken);
        }
    });
});
