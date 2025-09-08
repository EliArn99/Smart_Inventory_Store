document.addEventListener('DOMContentLoaded', function () {
    const updateBtns = document.getElementsByClassName("update-cart");
    const wishlistBtns = document.getElementsByClassName('btn-wishlist');

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');


    for (let i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener("click", function () {
            const productId = this.dataset.product;
            const action = this.dataset.action;
            console.log("productId:", productId, "Action:", action);

            if (user === "AnonymousUser") {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }
        });
    }

    function updateUserOrder(productId, action) {
        console.log("Потребителят е логнат, изпращане на данни...");

        const url = "/store/update_item/";
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ bookId: productId, action: action }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || response.statusText);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Данни от сървъра:", data);

            const cartTotalElement = document.getElementById("cart-total");
            if (cartTotalElement) {
                cartTotalElement.textContent = data.cartItems;
                // Добавена логика за показване/скриване на значката
                if (data.cartItems > 0) {
                    cartTotalElement.classList.remove('d-none');
                } else {
                    cartTotalElement.classList.add('d-none');
                }
                console.log("Обновен общ брой артикули в количката:", data.cartItems);
            } else {
                console.warn("Елемент с ID 'cart-total' не е намерен. Не може да се обнови броят на артикулите в количката динамично.");
            }

            // Презареждане само на страницата на количката
            if (window.location.pathname === '/store/cart/') {
                location.reload();
            }
        })
        .catch(error => {
            console.error("Грешка при fetch операцията:", error);
            // Показване на по-елегантен модал вместо alert
            showModalMessage("Възникна грешка при обновяване на количката. Моля, опитайте отново.", "error");
        });
    }

    function addCookieItem(productId, action) {
        console.log("Потребителят не е логнат, обновяване на бисквитки...");
        let cart = JSON.parse(getCookie('cart') || '{}');

        if (action === "add") {
            if (cart[productId] === undefined) {
                cart[productId] = { quantity: 1 };
            } else {
                cart[productId]["quantity"] += 1;
            }
        } else if (action === "remove") {
            if (cart[productId] && cart[productId]["quantity"] > 0) {
                cart[productId]["quantity"] -= 1;
            }

            if (cart[productId] && cart[productId]["quantity"] <= 0) {
                console.log("Артикулът трябва да бъде изтрит");
                delete cart[productId];
            }
        }

        console.log("КОЛИЧКА:", cart);
        document.cookie = `cart=${JSON.stringify(cart)};path=/`;

        // Обновяване на UI на количката веднага
        const totalItems = Object.values(cart).reduce((total, item) => total + item.quantity, 0);
        const cartTotalElement = document.getElementById("cart-total");
        if (cartTotalElement) {
            cartTotalElement.textContent = totalItems;
            // Добавена логика за показване/скриване на значката
            if (totalItems > 0) {
                cartTotalElement.classList.remove('d-none');
            } else {
                cartTotalElement.classList.add('d-none');
            }
        }

        // Презареждане на страницата на количката, за да се покажат промените
        if (window.location.pathname === '/store/cart/') {
            location.reload();
        }
    }


    for (let i = 0; i < wishlistBtns.length; i++) {
        wishlistBtns[i].addEventListener('click', function (e) {
            e.preventDefault();

            const btn = this;
            const bookId = btn.dataset.book;
            const action = btn.dataset.action;
            console.log('Book ID:', bookId, 'Action:', action);

            if (user === 'AnonymousUser') {
                console.log('Потребителят не е логнат');
                showModalMessage("Трябва да сте логнат, за да добавяте книги в списъка с желания.", "warning");
                return;
            }

            updateWishlist(bookId, action, btn);
        });
    }

    function updateWishlist(bookId, action, btn) {
        console.log('Изпращане на заявка за wishlist...');
        const url = '/store/update_wishlist/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 'bookId': bookId, 'action': action })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || response.statusText);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Данни:', data);

            const heartIcon = btn.querySelector('i');

            if (data.added) {
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas', 'text-danger');
                btn.dataset.action = 'remove';
            } else {
                heartIcon.classList.remove('fas', 'text-danger');
                heartIcon.classList.add('far');
                btn.dataset.action = 'add';
            }
        })
        .catch(error => {
            console.error('Възникна проблем с fetch операцията:', error);
            showModalMessage("Възникна грешка при обновяване на списъка с желания.", "error");
        });
    }


    const form = document.getElementById('form');
    const formButton = document.getElementById('form-button');
    const paypalButtonContainer = document.getElementById('paypal-button-container');

    if (formButton && paypalButtonContainer) {
        formButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Бутонът за плащане е натиснат');
            formButton.classList.add('d-none');
            paypalButtonContainer.classList.remove('d-none');
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Формата е изпратена...');
            submitFormData();
        });
    }

    function submitFormData() {
        console.log('Изпращане на данни за поръчката...');
        const url = '/store/process_order/';

        const userFormData = {
            'name': form.name.value,
            'email': form.email.value,
        };

        const shippingInfo = {
            'address': form.address.value,
            'city': form.city.value,
            'state': form.state.value,
            'zipcode': form.zipcode.value,
        };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 'form': userFormData, 'shipping': shippingInfo })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || response.statusText);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            showModalMessage("Поръчката беше успешно завършена!", "success");

            document.cookie = 'cart=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

            setTimeout(() => {
                window.location.href = "/store/store/";
            }, 3000);
        })
        .catch(error => {
            console.error('Грешка:', error);
            showModalMessage("Възникна грешка при обработка на поръчката. Моля, опитайте отново.", "error");
        });
    }


    function showModalMessage(message, type) {
        const modal = document.getElementById('messageModal');
        const modalText = document.getElementById('modalMessageText');
        const modalHeader = document.getElementById('modalMessageHeader');

        if (!modal || !modalText || !modalHeader) {
            console.error("Не са намерени елементи за модала. Използвайте `alert()` като алтернатива.");
            alert(message);
            return;
        }

        let headerText = '';
        let headerColor = '';
        let iconHtml = '';

        switch (type) {
            case 'success':
                headerText = 'Успех!';
                headerColor = 'text-success';
                iconHtml = '<i class="fas fa-check-circle me-2"></i>';
                break;
            case 'error':
                headerText = 'Грешка!';
                headerColor = 'text-danger';
                iconHtml = '<i class="fas fa-times-circle me-2"></i>';
                break;
            case 'warning':
                headerText = 'Внимание!';
                headerColor = 'text-warning';
                iconHtml = '<i class="fas fa-exclamation-triangle me-2"></i>';
                break;
            default:
                headerText = 'Информация';
                headerColor = '';
                iconHtml = '<i class="fas fa-info-circle me-2"></i>';
                break;
        }

        modalHeader.className = `modal-title d-flex align-items-center ${headerColor}`;
        modalHeader.innerHTML = `${iconHtml}${headerText}`;
        modalText.textContent = message;

        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }


});
