export function ensureMessageModal() {
    if (document.getElementById("messageModal")) {
        return;
    }

    document.body.insertAdjacentHTML(
        "beforeend",
        `
        <div class="modal fade" id="messageModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="modalMessageHeader"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <p id="modalMessageText"></p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Затвори</button>
              </div>
            </div>
          </div>
        </div>
        `
    );
}

export function showModalMessage(message, type = "info") {
    const modal = document.getElementById("messageModal");
    const modalText = document.getElementById("modalMessageText");
    const modalHeader = document.getElementById("modalMessageHeader");

    if (!modal || !modalText || !modalHeader) {
        alert(message);
        return;
    }

    let headerText = "Информация";
    let headerColor = "";
    let iconHtml = '<i class="fas fa-info-circle me-2"></i>';

    if (type === "success") {
        headerText = "Успех!";
        headerColor = "text-success";
        iconHtml = '<i class="fas fa-check-circle me-2"></i>';
    } else if (type === "error") {
        headerText = "Грешка!";
        headerColor = "text-danger";
        iconHtml = '<i class="fas fa-times-circle me-2"></i>';
    } else if (type === "warning") {
        headerText = "Внимание!";
        headerColor = "text-warning";
        iconHtml = '<i class="fas fa-exclamation-triangle me-2"></i>';
    }

    modalHeader.className = `modal-title d-flex align-items-center ${headerColor}`;
    modalHeader.innerHTML = `${iconHtml}${headerText}`;
    modalText.textContent = message;

    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}
