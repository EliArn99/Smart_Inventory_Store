export function ensureMessageModal() {
    if (document.getElementById("messageModal")) return;
    document.body.insertAdjacentHTML("beforeend", `
        <div class="modal fade" id="messageModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header"><h5 class="modal-title" id="modalMessageHeader"></h5></div>
              <div class="modal-body"><p id="modalMessageText"></p></div>
              <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Затвори</button></div>
            </div>
          </div>
        </div>`);
}

export function showModalMessage(message, type = "info") {
    const modalText = document.getElementById("modalMessageText");
    const modalHeader = document.getElementById("modalMessageHeader");
    modalText.textContent = message;
    modalHeader.textContent = type === "success" ? "Успех!" : "Грешка!";
    const modalInstance = new bootstrap.Modal(document.getElementById("messageModal"));
    modalInstance.show();
}
