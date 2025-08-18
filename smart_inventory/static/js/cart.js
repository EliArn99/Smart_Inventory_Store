//
// document.addEventListener('DOMContentLoaded', function() {
//     var updateBtns = document.getElementsByClassName("update-cart");
//
//     for (i = 0; i < updateBtns.length; i++) {
//         updateBtns[i].addEventListener("click", function () {
//             var productId = this.dataset.product;
//             var action = this.dataset.action;
//             console.log("productId:", productId, "Action:", action);
//             console.log("USER:", user); //
//
//             if (user == "AnonymousUser") {
//                 addCookieItem(productId, action);
//             } else {
//                 updateUserOrder(productId, action);
//             }
//         });
//     }
//
//     function updateUserOrder(productId, action) {
//         console.log("User is authenticated, sending data...");
//
//         var url = "/store/update_item/";
//         fetch(url, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrftoken,
//             },
//             body: JSON.stringify({ bookId: productId, action: action }),
//         })
//         .then((response) => {
//             if (!response.ok) {
//
//                 return response.json().then(errorData => {
//                     throw new Error(errorData.error || response.statusText);
//                 });
//             }
//             return response.json();
//         })
//         .then((data) => {
//             console.log("Data from server:", data);
//
//
//             var cartTotalElement = document.getElementById("cart-total");
//             if (cartTotalElement) {
//                 cartTotalElement.textContent = data.cartItems;
//                 console.log("Updated cart total to:", data.cartItems);
//             } else {
//                 console.warn("Element with ID 'cart-total' not found. Cannot update cart total dynamically.");
//             }
//
//
//             if (window.location.pathname === '/store/cart/') {
//                  location.reload();
//             }
//
//             // ------------------------------------
//         })
//         .catch((error) => {
//             console.error("Error during fetch operation:", error);
//         });
//     }
//
//     function addCookieItem(productId, action) {
//         console.log("User is not authenticated");
//
//         if (action == "add") {
//             if (cart[productId] == undefined) {
//                 cart[productId] = { quantity: 1 };
//             } else {
//                 cart[productId]["quantity"] += 1;
//             }
//         }
//
//         if (action == "remove") {
//             cart[productId]["quantity"] -= 1;
//
//             if (cart[productId]["quantity"] <= 0) {
//                 console.log("Item should be deleted");
//                 delete cart[productId];
//             }
//         }
//         console.log("CART:", cart);
//         document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
//
//         location.reload();
//     }
// });
//


document.addEventListener('DOMContentLoaded', function () {
    var updateBtns = document.getElementsByClassName("update-cart");

    for (i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener("click", function () {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            console.log("productId:", productId, "Action:", action);
            console.log("USER:", user); //

            if (user == "AnonymousUser") {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }
        });
    }

    function updateUserOrder(productId, action) {
        console.log("User is authenticated, sending data...");

        var url = "/store/update_item/";
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({bookId: productId, action: action}),
        })
            .then((response) => {
                if (!response.ok) {

                    return response.json().then(errorData => {
                        throw new Error(errorData.error || response.statusText);
                    });
                }
                return response.json();
            })
            .then((data) => {
                console.log("Data from server:", data);


                var cartTotalElement = document.getElementById("cart-total");
                if (cartTotalElement) {
                    cartTotalElement.textContent = data.cartItems;
                    console.log("Updated cart total to:", data.cartItems);
                } else {
                    console.warn("Element with ID 'cart-total' not found. Cannot update cart total dynamically.");
                }


                if (window.location.pathname === '/store/cart/') {
                    location.reload();
                }

                // ------------------------------------
            })
            .catch((error) => {
                console.error("Error during fetch operation:", error);
            });
    }

    function addCookieItem(productId, action) {
        console.log("User is not authenticated");

        if (action == "add") {
            if (cart[productId] == undefined) {
                cart[productId] = {quantity: 1};
            } else {
                cart[productId]["quantity"] += 1;
            }
        }

        if (action == "remove") {
            cart[productId]["quantity"] -= 1;

            if (cart[productId]["quantity"] <= 0) {
                console.log("Item should be deleted");
                delete cart[productId];
            }
        }
        console.log("CART:", cart);
        document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

        location.reload();
    }
});


const wishlistBtns = document.getElementsByClassName('btn-wishlist');

for (let i = 0; i < wishlistBtns.length; i++) {
    wishlistBtns[i].addEventListener('click', function (e) {
        if (!e.target.closest('.btn-wishlist')) return;

        const btn = e.target.closest('.btn-wishlist');
        const bookId = btn.dataset.book;
        const action = btn.dataset.action;
        console.log('Book ID:', bookId, 'Action:', action);

        if (user === 'AnonymousUser') {
            console.log('Потребителят не е логнат');
            return;
        }

        updateWishlist(bookId, action);
    });
}

function updateWishlist(bookId, action) {
    console.log('Изпращане на заявка за wishlist...');
    const url = '/store/update_wishlist/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'bookId': bookId, 'action': action})
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data:', data);

            const btn = document.querySelector(`.btn-wishlist[data-book="${bookId}"]`);
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
            console.error('There was a problem with the fetch operation:', error);
            alert('Възникна грешка при обновяване на списъка с желания.');
        });
}


function submitFormData(){
    console.log('Payment button clicked');

    var userFormData = {
        'name': form.name.value,
        'email': form.email.value,
        'total': total,
    }

    var shippingInfo = {
        'address': form.address.value,
        'city': form.city.value,
        'state': form.state.value,
        'zipcode': form.zipcode.value,
    }

    var url = '/store/process_order/'

    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'form':userFormData, 'shipping':shippingInfo})
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success:', data);
        alert('Поръчката беше успешно завършена!');

        // 1. Почистете количката в JavaScript
        document.cookie = 'cart=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

        // 2. Обновете броя на артикулите в навигационната лента
        document.getElementById("cart-total").textContent = "0";

        // 3. Пренасочете потребителя към страница с потвърждение
        window.location.href = "{% url 'store:store' %}"; // Можете да създадете страница с "Благодаря за поръчката!"

    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Възникна грешка при обработка на поръчката. Моля, опитайте отново.');
    });
}
