from datetime import time
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import FormView
from .forms import CustomUserCreationForm, ReviewForm, PostForm, CommentForm
from .models import Book, Order, OrderItem, Category, WishlistItem, Review, ShippingAddress, Post, Banner, \
    BlogCategory
import json
from .utils import cartData, cookieCart, guestOrder
from django.db.models import Q, Count, Avg, F


class CartMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = cartData(self.request)
        context['cartItems'] = data['cartItems']
        context['order'] = data['order']
        context['items'] = data['items']
        return context


class BaseContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = cartData(self.request)
        context['cartItems'] = data['cartItems']
        return context


class BookListView(BaseContextMixin, ListView):
    model = Book
    template_name = 'store/store.html'
    context_object_name = 'books_on_page'
    paginate_by = 12

    def get_queryset(self):
        books = Book.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).annotate(
            reviews_count=Count('reviews')
        )

        query = self.request.GET.get('q')
        if query:
            books = books.filter(
                Q(name__icontains=query) |
                Q(author__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            books = books.filter(category__slug=category_slug)

        author = self.request.GET.get('author')
        if author:
            books = books.filter(author__icontains=author)

        year = self.request.GET.get('year')
        if year:
            try:
                books = books.filter(publication_year=int(year))
            except (ValueError, TypeError):
                pass

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            books = books.filter(price__gte=min_price)
        if max_price:
            books = books.filter(price__lte=max_price)

        sort_by = self.request.GET.get('sort_by', 'name')
        order = self.request.GET.get('order', 'asc')

        valid_sort_fields = ['name', 'price', 'avg_rating', 'publication_year']
        if sort_by in valid_sort_fields:
            if order == 'desc':
                books = books.order_by(F(sort_by).desc(nulls_last=True))
            else:
                books = books.order_by(F(sort_by).asc(nulls_last=True))
        else:
            books = books.order_by('name')

        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(book_count=Count('book'))
        context['banners'] = Banner.objects.filter(is_active=True)
        context['active_category_slug'] = self.kwargs.get('category_slug')
        context['query'] = self.request.GET.get('q')
        context['min_price'] = self.request.GET.get('min_price')
        context['max_price'] = self.request.GET.get('max_price')
        context['author'] = self.request.GET.get('author')
        context['year'] = self.request.GET.get('year')
        context['sort_by'] = self.request.GET.get('sort_by', 'name')
        context['order'] = self.request.GET.get('order', 'asc')
        return context


class AboutUsView(BaseContextMixin, TemplateView):
    template_name = 'store/about_us.html'


class CartView(CartMixin, TemplateView):
    template_name = 'store/cart.html'


class CheckoutView(CartMixin, TemplateView):
    template_name = 'store/checkout.html'


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

        order_items = order.orderitem_set.all()
        for item in order_items:
            book = item.product
            if book.stock < item.quantity:
                return JsonResponse(
                    {'error': f'Недостатъчна наличност за книга "{book.name}".'},
                    status=400
                )

        order.complete = True

        for item in order_items:
            book = item.product
            book.stock -= item.quantity
            book.save()

        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                zipcode=data['shipping']['zipcode'],
            )

        response = JsonResponse('Payment submitted successfully', safe=False)
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


class BookDetailView(BaseContextMixin, DetailView, FormView):
    model = Book
    template_name = 'store/book_detail.html'
    context_object_name = 'book'
    pk_url_kwarg = 'pk'
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Трябва да сте влезли, за да оставите ревю.')
            return redirect('login')

        book = self.get_object()
        if Review.objects.filter(book=book, user=request.user).exists():
            messages.warning(request, 'Вече сте оставили ревю за тази книга.')
            return redirect('store:book_detail', pk=book.pk)

        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Вашето ревю беше успешно добавено!')
            return redirect('store:book_detail', pk=book.pk)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


@login_required
@require_POST
def update_wishlist(request):
    try:
        data = json.loads(request.body)
        book_id = data.get('bookId')
        action = data.get('action')

        if not all([book_id, action]):
            return JsonResponse({'error': 'Missing bookId or action'}, status=400)

        book = get_object_or_404(Book, id=book_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

        if action == 'add':
            message = 'Книгата е добавена в списъка с желания.' if created else 'Книгата вече е в списъка с желания.'
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
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'wishlist_items': user_wishlist, 'cartItems': cartItems}
    return render(request, 'store/wishlist.html', context)


class BlogListView(BaseContextMixin, ListView):
    model = Post
    template_name = 'store/blog_list.html'
    context_object_name = 'posts_list'
    paginate_by = 6
    queryset = Post.objects.filter(status=1).order_by('-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        return context


class PostsByCategoryView(BlogListView):
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        self.category = get_object_or_404(BlogCategory, slug=category_slug)
        return Post.objects.filter(category=self.category, status=1).order_by('-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.category
        return context


class BlogDetailView(BaseContextMixin, DetailView, FormView):
    model = Post
    template_name = 'store/blog_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(Post, slug=self.kwargs.get('slug'), status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True).order_by('-created_on')
        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Трябва да сте влезли, за да коментирате.')
            return redirect('login')

        new_comment = form.save(commit=False)
        new_comment.post = self.get_object()
        new_comment.user = self.request.user
        new_comment.save()
        messages.success(self.request, 'Вашият коментар е изпратен и очаква одобрение.')
        return redirect('store:blog_detail', slug=self.kwargs.get('slug'))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


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
    if not request.user.is_authenticated or order.customer != request.user.customer:
        raise Http404("You don't have permission to view this order.")

    context = {
        'order': order,
        'order_items': order.orderitem_set.all(),
    }
    return render(request, 'store/order_detail.html', context)
