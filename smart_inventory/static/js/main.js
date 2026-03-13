import { getCookie } from "./core/cookies.js";
import { ensureMessageModal } from "./ui/modal.js";
import { initCheckout } from "./cart/checkout.js";

document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = getCookie("csrftoken");

    ensureMessageModal();
    initCheckout(csrfToken);
});
