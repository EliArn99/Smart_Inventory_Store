export function updateCartBadge(count) {
    const badge = document.getElementById("cart-total");
    if (!badge) return;

    const safeCount = Number(count) || 0;

    badge.textContent = safeCount;

    if (safeCount > 0) {
        badge.classList.remove("d-none");
    } else {
        badge.classList.add("d-none");
    }
}
