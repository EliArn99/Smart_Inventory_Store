# from datetime import time
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse, Http404
# from django.shortcuts import render, get_object_or_404, redirect
# from django.views.decorators.http import require_POST
# from django.contrib import messages
# from .forms import CustomUserCreationForm, ReviewForm, PostForm, CommentForm
# from .models import Book, Order, OrderItem, Category, WishlistItem, Review, ShippingAddress, Post, Banner
# import json
# from .utils import cartData, cookieCart
# from django.db.models import Q, Count, Avg, F
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#
#
# def store(request, category_slug=None):
#     books = Book.objects.all()
#
#     books = books.annotate(
#         avg_rating=Avg('reviews__rating')
#     ).annotate(
#         reviews_count=Count('reviews')
#     )
#
#     query = request.GET.get('q')
#     if query:
#         books = books.filter(
#             Q(name__icontains=query) |
#             Q(author__icontains=query) |
#             Q(description__icontains=query)
#         ).distinct()
#
#     if category_slug:
#         books = books.filter(category__slug=category_slug)
#
#     author = request.GET.get('author')
#     if author:
#         books = books.filter(author__icontains=author)
#
#     year = request.GET.get('year')
#     if year:
#         try:
#             books = books.filter(publication_year=int(year))
#         except (ValueError, TypeError):
#             pass
#
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     if min_price:
#         books = books.filter(price__gte=min_price)
#     if max_price:
#         books = books.filter(price__lte=max_price)
#
#     sort_by = request.GET.get('sort_by', 'name')
#     order = request.GET.get('order', 'asc')
#
#     valid_sort_fields = ['name', 'price', 'avg_rating', 'publication_year']
#     if sort_by in valid_sort_fields:
#         if order == 'desc':
#             books = books.order_by(F(sort_by).desc(nulls_last=True))
#         else:
#             books = books.order_by(F(sort_by).asc(nulls_last=True))
#     else:
#         books = books.order_by('name')
#
#     paginator = Paginator(books, 12)
#     page = request.GET.get('page')
#     try:
#         books_on_page = paginator.page(page)
#     except PageNotAnInteger:
#         books_on_page = paginator.page(1)
#     except EmptyPage:
#         books_on_page = paginator.page(paginator.num_pages)
#
#     categories = Category.objects.annotate(book_count=Count('book'))
#     data = cartData(request)
#     cartItems = data['cartItems']
#     banners = Banner.objects.filter(is_active=True)
#
#     context = {
#         'books': books_on_page,
#         'cartItems': cartItems,
#         'categories': categories,
#         'active_category_slug': category_slug,
#         'query': query,
#         'min_price': min_price,
#         'max_price': max_price,
#         'author': author,
#         'year': year,
#         'sort_by': sort_by,
#         'order': order,
#         'banners': banners
#     }
#     return render(request, 'store/store.html', context)
#
#
# def about_us(request):
#     return render(request, 'store/about_us.html')
#
#
# def cart(request):
#     data = cartData(request)
#     cartItems = data['cartItems']
#     order = data['order']
#     items = data['items']
#
#     context = {'items': items, 'order': order, 'cartItems': cartItems}
#     return render(request, 'store/cart.html', context)
#
#
# def checkout(request):
#     data = cartData(request)
#     cartItems = data['cartItems']
#     order = data['order']
#     items = data['items']
#
#     context = {'items': items, 'order': order, 'cartItems': cartItems}
#     return render(request, 'store/checkout.html', context)
#
#
# @require_POST
# def updateItem(request):
#     data = json.loads(request.body)
#     bookId = data.get('bookId')
#     action = data.get('action')
#
#     book = get_object_or_404(Book, pk=bookId)
#
#     if request.user.is_authenticated:
#         customer = request.user.customer
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)
#         orderItem, created = OrderItem.objects.get_or_create(order=order, product=book)
#
#         if action == 'add':
#             orderItem.quantity = (orderItem.quantity + 1)
#         elif action == 'remove':
#             orderItem.quantity = (orderItem.quantity - 1)
#         orderItem.save()
#
#         if orderItem.quantity <= 0:
#             orderItem.delete()
#
#         cartItems = order.get_cart_items
#         return JsonResponse({'cartItems': cartItems}, safe=False)
#
#     else:
#         print('User is not authenticated')
#         cookie_data = cookieCart(request)
#         cart = cookie_data['cart']
#
#         if action == 'add':
#             quantity = cart.get(bookId, {'quantity': 0})['quantity'] + 1
#             cart[bookId] = {'quantity': quantity}
#
#         elif action == 'remove':
#             if bookId in cart:
#                 cart[bookId]['quantity'] -= 1
#                 if cart[bookId]['quantity'] <= 0:
#                     del cart[bookId]
#
#         cart_items_count = sum(item['quantity'] for item in cart.values())
#
#         response = JsonResponse({'cartItems': cart_items_count}, safe=False)
#
#         response.set_cookie('cart', json.dumps(cart))
#
#         return response
#
#
# # def processOrder(request):
# #     data = json.loads(request.body)
# #     transaction_id = str(int(time.time() * 1000))
# #     customer = request.user.customer
# #
# #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
# #     total = float(data['form']['total'])
# #     order.transaction_id = transaction_id
# #
# #     if total == order.get_cart_total:
# #         order.complete = True
# #
# #         for item in order.orderitem_set.all():
# #             book = item.product
# #             if book.stock >= item.quantity:
# #                 book.stock -= item.quantity
# #                 book.save()
# #             else:
# #                 return JsonResponse({'error': f'Недостатъчна наличност за книга "{book.name}".'}, status=400)
# #
# #         order.save()
# #
# #     if order.shipping == True:
# #         ShippingAddress.objects.create(
# #             customer=customer,
# #             order=order,
# #             address=data['shipping']['address'],
# #             city=data['shipping']['city'],
# #             state=data['shipping']['state'],
# #             zipcode=data['shipping']['zipcode'],
# #         )
# #
# #     return JsonResponse('Payment submitted..', safe=False)
#
# def processOrder(request):
#     transaction_id = str(int(time.time() * 1000))
#     data = json.loads(request.body)
#
#     if request.user.is_authenticated:
#         customer = request.user.customer
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)
#     else:
#         # Използваме guestOrder, за да създадем или намерим анонимен потребител и поръчка
#         customer, order = guestOrder(request, data)
#
#     total = float(data['form']['total'])
#     order.transaction_id = transaction_id
#
#     if total == float(order.get_cart_total): # Уверете се, че типовете данни съвпадат
#         order.complete = True
#         order.save()
#
#         # Намаляване на наличността на продуктите
#         order_items = order.orderitem_set.all()
#         for item in order_items:
#             book = item.product
#             if book.stock >= item.quantity:
#                 book.stock -= item.quantity
#                 book.save()
#             else:
#                 return JsonResponse({'error': f'Недостатъчна наличност за книга "{book.name}".'}, status=400)
#
#         # Създаване на адрес за доставка
#         ShippingAddress.objects.create(
#             customer=customer,
#             order=order,
#             address=data['shipping']['address'],
#             city=data['shipping']['city'],
#             zipcode=data['shipping']['zipcode'],
#         )
#
#         # Добавете логика за изчистване на количката за анонимни потребители
#         if not request.user.is_authenticated:
#             # Трябва да изчистим бисквитката след успешно завършване на поръчката
#             response = JsonResponse('Payment submitted..', safe=False)
#             response.delete_cookie('cart')
#             return response
#
#     return JsonResponse('Payment submitted..', safe=False)
#
#
# def get_cart_data(request):
#     data = cartData(request)
#     data['order']['get_cart_total'] = float(data['order']['get_cart_total'])
#     for item in data['items']:
#         item['product']['price'] = float(item['product']['price'])
#         item['get_total'] = float(item['get_total'])
#     return JsonResponse(data, safe=False)
#
#
# # store/views.py
#
# @login_required
# def profile_details(request):
#     customer = request.user.customer
#     orders = customer.order_set.all().order_by('-date_ordered')
#
#     purchased_categories = Category.objects.filter(
#         book__orderitem__order__customer=customer
#     ).distinct()
#
#     recommended_books = Book.objects.filter(
#         category__in=purchased_categories
#     ).exclude(
#         orderitem__order__customer=customer
#     ).order_by('?')
#
#     if not recommended_books:
#         recommended_books = Book.objects.all().order_by('?')[:4]
#     else:
#         recommended_books = recommended_books[:4]
#
#     context = {
#         'customer': customer,
#         'orders': orders,
#         'recommended_books': recommended_books,
#     }
#     return render(request, 'store/profile_details.html', context)
#
#
# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('store:store')
#
#     else:
#         form = CustomUserCreationForm()
#
#     context = {'form': form}
#     return render(request, 'registration/register.html', context)
#
#
# def book_detail(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     data = cartData(request)
#     cartItems = data['cartItems']
#
#     reviews = book.reviews.all().order_by('-created_at')
#
#     if request.method == 'POST':
#         if not request.user.is_authenticated:
#             messages.error(request, 'Трябва да сте влезли, за да оставите ревю.')
#             return redirect('login')
#
#         if Review.objects.filter(book=book, user=request.user).exists():
#             messages.warning(request, 'Вече сте оставили ревю за тази книга.')
#             return redirect('store:book_detail', pk=pk)
#
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.book = book
#             review.user = request.user
#             review.save()
#             messages.success(request, 'Вашето ревю беше успешно добавено!')
#             return redirect('store:book_detail', pk=pk)
#     else:
#         form = ReviewForm()
#
#     context = {
#         'book': book,
#         'cartItems': cartItems,
#         'reviews': reviews,
#         'form': form,
#     }
#     return render(request, 'store/book_detail.html', context)
#
#
# @login_required
# @require_POST
# def update_wishlist(request):
#     try:
#         data = json.loads(request.body)
#         book_id = data.get('bookId')
#         action = data.get('action')
#
#         if not all([book_id, action]):
#             return JsonResponse({'error': 'Missing bookId or action'}, status=400)
#
#         book = Book.objects.get(id=book_id)
#         wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)
#
#         if action == 'add':
#             if created:
#                 message = 'Книгата е добавена в списъка с желания.'
#                 added = True
#             else:
#                 message = 'Книгата вече е в списъка с желания.'
#                 added = True
#         elif action == 'remove':
#             if not created:
#                 wishlist_item.delete()
#                 message = 'Книгата е премахната от списъка с желания.'
#                 added = False
#             else:
#                 message = 'Книгата не е в списъка с желания.'
#                 added = False
#         else:
#             return JsonResponse({'error': 'Invalid action'}, status=400)
#
#         return JsonResponse({'message': message, 'added': added, 'book_id': book_id})
#
#     except Book.DoesNotExist:
#         return JsonResponse({'error': 'Book not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#
# @login_required(login_url='login')
# def wishlist_view(request):
#     user_wishlist = WishlistItem.objects.filter(user=request.user)
#     context = {'wishlist_items': user_wishlist}
#     return render(request, 'store/wishlist.html', context)
#
#
# def search_results(request):
#     data = cartData(request)
#     cartItems = data['cartItems']
#     query = request.GET.get('q')
#
#     books = Book.objects.all()
#
#     if query:
#         books = books.filter(
#             Q(name__icontains=query) |
#             Q(author__icontains=query) |
#             Q(description__icontains=query)
#         ).distinct()
#
#     context = {
#         'books': books,
#         'cartItems': cartItems,
#         'query': query,
#     }
#     return render(request, 'store/store.html', context)
#
#
# def blog_list(request):
#     posts_list = Post.objects.filter(status=1).order_by('-created_on')
#
#     paginator = Paginator(posts_list, 6)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'page_obj': page_obj,
#         'is_paginated': True,
#     }
#     return render(request, 'store/blog_list.html', context)
#
#
# def blog_detail(request, slug):
#     post = get_object_or_404(Post, slug=slug, status=1)
#
#     comments = post.comments.filter(is_approved=True).order_by('-created_on')
#
#     if request.method == 'POST':
#         if not request.user.is_authenticated:
#             messages.error(request, 'Трябва да сте влезли, за да коментирате.')
#             return redirect('login')
#
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post
#             new_comment.user = request.user
#             new_comment.save()
#             messages.success(request, 'Вашият коментар е изпратен и очаква одобрение.')
#             return redirect('store:blog_detail', slug=slug)
#     else:
#         comment_form = CommentForm()
#
#     context = {
#         'post': post,
#         'comments': comments,
#         'comment_form': comment_form,
#     }
#     return render(request, 'store/blog_detail.html', context)
#
#
# @staff_member_required
# def add_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             messages.success(request, 'Публикацията беше успешно създадена!')
#             return redirect('store:blog_list')
#     else:
#         form = PostForm()
#
#     return render(request, 'store/add_post.html', {'form': form})
#
#
# @staff_member_required
# def inventory_report_view(request):
#     low_stock_books = Book.objects.filter(stock__lte=5).order_by('stock')
#
#     context = {
#         'low_stock_books': low_stock_books,
#     }
#     return render(request, 'admin/inventory_report.html', context)
#
#
# def order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#
#
#     if order.customer != request.user.customer:
#         raise Http404("You don't have permission to view this order.")
#         pass
#
#     context = {
#         'order': order,
#         'order_items': order.orderitem_set.all(),  # Всички продукти в поръчката
#     }
#     return render(request, 'store/order_detail.html', context)


from datetime import time
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import CustomUserCreationForm, ReviewForm, PostForm, CommentForm
from .models import Book, Order, OrderItem, Category, WishlistItem, Review, ShippingAddress, Post, Banner, Customer
import json
from .utils import cartData, cookieCart, guestOrder
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def store(request, category_slug=None):
    books = Book.objects.all()

    books = books.annotate(
        avg_rating=Avg('reviews__rating')
    ).annotate(
        reviews_count=Count('reviews')
    )

    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(name__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    if category_slug:
        books = books.filter(category__slug=category_slug)

    author = request.GET.get('author')
    if author:
        books = books.filter(author__icontains=author)

    year = request.GET.get('year')
    if year:
        try:
            books = books.filter(publication_year=int(year))
        except (ValueError, TypeError):
            pass

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    valid_sort_fields = ['name', 'price', 'avg_rating', 'publication_year']
    if sort_by in valid_sort_fields:
        if order == 'desc':
            books = books.order_by(F(sort_by).desc(nulls_last=True))
        else:
            books = books.order_by(F(sort_by).asc(nulls_last=True))
    else:
        books = books.order_by('name')

    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    try:
        books_on_page = paginator.page(page)
    except PageNotAnInteger:
        books_on_page = paginator.page(1)
    except EmptyPage:
        books_on_page = paginator.page(paginator.num_pages)

    categories = Category.objects.annotate(book_count=Count('book'))
    data = cartData(request)
    cartItems = data['cartItems']
    banners = Banner.objects.filter(is_active=True)

    context = {
        'books': books_on_page,
        'cartItems': cartItems,
        'categories': categories,
        'active_category_slug': category_slug,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'author': author,
        'year': year,
        'sort_by': sort_by,
        'order': order,
        'banners': banners
    }
    return render(request, 'store/store.html', context)


def about_us(request):
    return render(request, 'store/about_us.html')


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


@require_POST
def updateItem(request):
    data = json.loads(request.body)
    bookId = data.get('bookId')
    action = data.get('action')

    book = get_object_or_404(Book, pk=bookId)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=book)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        cartItems = order.get_cart_items
        return JsonResponse({'cartItems': cartItems}, safe=False)

    else:
        print('User is not authenticated')
        cookie_data = cookieCart(request)
        cart = cookie_data['cart']

        if action == 'add':
            quantity = cart.get(bookId, {'quantity': 0})['quantity'] + 1
            cart[bookId] = {'quantity': quantity}

        elif action == 'remove':
            if bookId in cart:
                cart[bookId]['quantity'] -= 1
                if cart[bookId]['quantity'] <= 0:
                    del cart[bookId]

        cart_items_count = sum(item['quantity'] for item in cart.values())

        response = JsonResponse({'cartItems': cart_items_count}, safe=False)

        response.set_cookie('cart', json.dumps(cart))

        return response


@require_POST
def processOrder(request):
    transaction_id = str(int(time.time() * 1000))
    data = json.loads(request.body)

    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(order.get_cart_total)

        order.transaction_id = transaction_id

        # Проверка за наличност преди завършване на поръчката
        order_items = order.orderitem_set.all()
        for item in order_items:
            book = item.product
            if book.stock < item.quantity:
                return JsonResponse(
                    {'error': f'Недостатъчна наличност за книга "{book.name}".'},
                    status=400
                )

        order.complete = True

        # Намаляване на наличността след успешно завършване
        for item in order_items:
            book = item.product
            book.stock -= item.quantity
            book.save()

        order.save()

        # Създаване на адрес за доставка
        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                zipcode=data['shipping']['zipcode'],
            )

        response = JsonResponse('Payment submitted successfully', safe=False)

        # Изчистване на бисквитката "cart" за анонимни потребители
        if not request.user.is_authenticated:
            response.delete_cookie('cart')

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_cart_data(request):
    data = cartData(request)
    data['order']['get_cart_total'] = float(data['order']['get_cart_total'])
    for item in data['items']:
        item['product']['price'] = float(item['product']['price'])
        item['get_total'] = float(item['get_total'])
    return JsonResponse(data, safe=False)


# store/views.py

@login_required
def profile_details(request):
    customer = request.user.customer
    orders = customer.order_set.all().order_by('-date_ordered')

    purchased_categories = Category.objects.filter(
        book__orderitem__order__customer=customer
    ).distinct()

    recommended_books = Book.objects.filter(
        category__in=purchased_categories
    ).exclude(
        orderitem__order__customer=customer
    ).order_by('?')

    if not recommended_books:
        recommended_books = Book.objects.all().order_by('?')[:4]
    else:
        recommended_books = recommended_books[:4]

    context = {
        'customer': customer,
        'orders': orders,
        'recommended_books': recommended_books,
    }
    return render(request, 'store/profile_details.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:store')

    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    data = cartData(request)
    cartItems = data['cartItems']

    reviews = book.reviews.all().order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Трябва да сте влезли, за да оставите ревю.')
            return redirect('login')

        if Review.objects.filter(book=book, user=request.user).exists():
            messages.warning(request, 'Вече сте оставили ревю за тази книга.')
            return redirect('store:book_detail', pk=pk)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Вашето ревю беше успешно добавено!')
            return redirect('store:book_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'book': book,
        'cartItems': cartItems,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'store/book_detail.html', context)


@login_required
@require_POST
def update_wishlist(request):
    try:
        data = json.loads(request.body)
        book_id = data.get('bookId')
        action = data.get('action')

        if not all([book_id, action]):
            return JsonResponse({'error': 'Missing bookId or action'}, status=400)

        book = Book.objects.get(id=book_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

        if action == 'add':
            if created:
                message = 'Книгата е добавена в списъка с желания.'
                added = True
            else:
                message = 'Книгата вече е в списъка с желания.'
                added = True
        elif action == 'remove':
            if not created:
                wishlist_item.delete()
                message = 'Книгата е премахната от списъка с желания.'
                added = False
            else:
                message = 'Книгата не е в списъка с желания.'
                added = False
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        return JsonResponse({'message': message, 'added': added, 'book_id': book_id})

    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='login')
def wishlist_view(request):
    user_wishlist = WishlistItem.objects.filter(user=request.user)
    context = {'wishlist_items': user_wishlist}
    return render(request, 'store/wishlist.html', context)


def search_results(request):
    data = cartData(request)
    cartItems = data['cartItems']
    query = request.GET.get('q')

    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(name__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'books': books,
        'cartItems': cartItems,
        'query': query,
    }
    return render(request, 'store/store.html', context)


def blog_list(request):
    posts_list = Post.objects.filter(status=1).order_by('-created_on')

    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'is_paginated': True,
    }
    return render(request, 'store/blog_list.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=1)

    comments = post.comments.filter(is_approved=True).order_by('-created_on')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Трябва да сте влезли, за да коментирате.')
            return redirect('login')

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Вашият коментар е изпратен и очаква одобрение.')
            return redirect('store:blog_detail', slug=slug)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'store/blog_detail.html', context)


@staff_member_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикацията беше успешно създадена!')
            return redirect('store:blog_list')
    else:
        form = PostForm()

    return render(request, 'store/add_post.html', {'form': form})


@staff_member_required
def inventory_report_view(request):
    low_stock_books = Book.objects.filter(stock__lte=5).order_by('stock')

    context = {
        'low_stock_books': low_stock_books,
    }
    return render(request, 'admin/inventory_report.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.customer != request.user.customer:
        raise Http404("You don't have permission to view this order.")
        pass

    context = {
        'order': order,
        'order_items': order.orderitem_set.all(),
    }
    return render(request, 'store/order_detail.html', context)
