// static/js/wishlist.js

// Уверете се, че променливите csrftoken и user са достъпни глобално
// от base.html, където ги дефинирате.
// Например:
// <script>
//     var user = '{{ request.user }}';
//     var csrftoken = '{{ csrf_token }}';
// </script>

document.addEventListener('DOMContentLoaded', function() {
    var updateWishlistBtns = document.getElementsByClassName('update-wishlist-btn');

    for (var i = 0; i < updateWishlistBtns.length; i++) {
        updateWishlistBtns[i].addEventListener('click', function(){
            var bookId = this.dataset.book;
            var action = this.dataset.action;

            if (user === 'AnonymousUser'){
                alert('Трябва да сте влезли, за да променяте списъка си с желания.');
            } else {
                updateUserWishlist(bookId, action);
            }
        });
    }
});

function updateUserWishlist(bookId, action){
    console.log('User is logged in, sending data for wishlist...');
    var url = '/store/update_wishlist/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'bookId': bookId, 'action': action})
    })
    .then((response) => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error || 'Network response was not ok');
            });
        }
        return response.json();
    })
    .then((data) => {
        console.log('Wishlist update data:', data);

        // Презареждаме страницата, за да отразим промяната.
        // Това е най-лесният начин да актуализирате списъка.
        location.reload();
    })
    .catch((error) => {
        console.error('Error during fetch operation:', error);
        alert('Възникна грешка при обновяване на списъка с желания.');
    });
}