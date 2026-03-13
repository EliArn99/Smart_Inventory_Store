export function updateCartBadge(count) {

    const badge = document.getElementById("cart-total");

    if (!badge) return;

    badge.textContent = count;

    badge.classList.toggle("d-none", count <= 0);
}
