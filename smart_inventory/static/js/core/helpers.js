import { getCookie } from "./cookies.js";

export function isAnonymousUser() {
    return !window.user || window.user === "AnonymousUser";
}

export function getGuestCart() {
    try {
        const cart = getCookie("cart");
        return cart ? JSON.parse(cart) : {};
    } catch (error) {
        console.error("Invalid cart cookie:", error);
        return {};
    }
}

export function saveGuestCart(cart) {
    document.cookie = `cart=${encodeURIComponent(JSON.stringify(cart))}; path=/`;
}

export function updateGuestCart(productId, action) {
    const cart = getGuestCart();

    if (action === "add") {
        if (cart[productId]) {
            cart[productId].quantity += 1;
        } else {
            cart[productId] = { quantity: 1 };
        }
    } else if (action === "remove") {
        if (cart[productId]) {
            cart[productId].quantity -= 1;

            if (cart[productId].quantity <= 0) {
                delete cart[productId];
            }
        }
    } else if (action === "delete") {
        delete cart[productId];
    }

    saveGuestCart(cart);
    return cart;
}

export function getGuestCartItemsCount(cart = null) {
    const currentCart = cart || getGuestCart();

    return Object.values(currentCart).reduce((total, item) => {
        return total + (item.quantity || 0);
    }, 0);
}
