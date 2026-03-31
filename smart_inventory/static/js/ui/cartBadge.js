export function updateCartBadge(count) {
    const badge = document.getElementById("cart-total");
    if (!badge) return;

    badge.textContent = count;
    // Скрива значката, ако няма продукти (използва Bootstrap клас d-none)
    if (count > 0) {
        badge.classList.remove("d-none");
    } else {
        badge.classList.add("d-none");
    }
}
