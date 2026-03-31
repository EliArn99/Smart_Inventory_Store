import { getCookie } from "./core/cookies.js";
import { ensureMessageModal } from "./ui/modal.js";
import { initCheckout } from "./cart/checkout.js";
import { updateCart } from "./cart/cart.js";
import { updateWishlist } from "./cart/wishlist.js";

document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = getCookie("csrftoken");

    // Инициализира модала за съобщения
    ensureMessageModal();

    // Инициализира формата за плащане (ако съществува на страницата)
    initCheckout(csrfToken);

    // Глобален слушател за бутони (Event Delegation)
    document.addEventListener("click", (e) => {
        // Бутон за количка
        const cartBtn = e.target.closest(".update-cart");
        if (cartBtn) {
            const productId = cartBtn.dataset.product;
            const action = cartBtn.dataset.action;
            updateCart(productId, action, csrfToken);
        }

        // Бутон за списък с желания
        const wishlistBtn = e.target.closest(".update-wishlist");
        if (wishlistBtn) {
            const bookId = wishlistBtn.dataset.book;
            const action = wishlistBtn.dataset.action;
            updateWishlist(bookId, action, csrfToken);
        }
    });
});
