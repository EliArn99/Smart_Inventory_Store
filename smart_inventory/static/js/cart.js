var updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log("productId:", productId, "Action:", action);
        console.log("USER:", user);

        if (user == "AnonymousUser") {
            addCookieItem(productId, action);
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function updateUserOrder(productId, action) {
    console.log("User is authenticated, sending data...");

    var url = "/update_item/";

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ productId: productId, action: action }),
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            location.reload();
        });
}

function addCookieItem(productId, action) {
    console.log("User is not authenticated");

    if (action == "add") {
        if (cart[productId] == undefined) {
            cart[productId] = { quantity: 1 };
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




document.addEventListener('DOMContentLoaded', function() {
    var updateWishlistBtns = document.getElementsByClassName('update-wishlist');

    for (var i = 0; i < updateWishlistBtns.length; i++) {
        updateWishlistBtns[i].addEventListener('click', function(e) {
            // *** THIS LINE IS CRUCIAL ***
            e.preventDefault(); // Prevents the default browser action (GET request)

            var productId = this.dataset.product;
            var action = this.dataset.action;

            console.log('WISHLIST PRODUCT ID:', productId, 'ACTION:', action);

            // Ensure 'user' is correctly defined globally in base.html
            if (user === 'AnonymousUser') {
                console.log('User is not authenticated for wishlist. Redirecting to login...');
                window.location.href = '/login/';
                return;
            }

            updateUserWishlist(productId, action);
        });
    }
});

// Example in store/main.js or within a <script> tag in base.html
// Ensure this script runs after the DOM is loaded.

var updateWishlistBtns = document.getElementsByClassName('update-wishlist');

for (i = 0; i < updateWishlistBtns.length; i++) {
    updateWishlistBtns[i].addEventListener('click', function(e){
        e.preventDefault(); // Prevent the default anchor behavior (i.e., prevent href="#" from reloading/scrolling)
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId:', productId, 'action:', action);

        // This function should be defined somewhere, similar to your 'updateUserOrder' for cart
        updateUserWishlist(productId, action);
    });
}

function updateUserWishlist(productId, action){
    console.log('User is logged in, sending data...');

    var url = '/update_wishlist/'; // Make sure this matches your urls.py

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken, // Make sure 'csrftoken' is defined and retrieved
        },
        body:JSON.stringify({'productId':productId, 'action':action})
    })
    .then((response) => {
       return response.json();
    })
    .then((data) => {
        console.log('data:', data);
        alert(data.message); // Provide user feedback
        // You might want to change the icon or text here based on success/failure
        // location.reload(); // Uncomment if you want to refresh the page after adding/removing
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while updating wishlist.');
    });
}

