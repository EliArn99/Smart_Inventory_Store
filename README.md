# Smart Inventory Store 🛒

Smart Inventory Store is a full-stack Django e-commerce and inventory management application built with Django, PostgreSQL, Docker, Bootstrap and vanilla JavaScript.

The project includes a public storefront, shopping cart, checkout flow, wishlist, reviews, blog system, admin inventory management, low-stock email alerts and Docker-based deployment setup.

---

## Tech Stack

- Python 3
- Django 5.2
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- Gunicorn
- Nginx
- Whitenoise
- Bootstrap
- Vanilla JavaScript
- HTML/CSS

---

## Features

### Storefront
- Product listing with pagination
- Search by title, author and description
- Category filtering
- Price, author and year filters
- Sorting by name, price, rating and publication year
- Product detail page
- Product reviews and ratings

### Cart & Orders
- Authenticated user cart
- Guest cart using cookies
- Add/remove cart items
- Checkout flow
- Stock validation before order completion
- Automatic stock reduction after successful order
- Shipping address creation when required

### User Features
- Registration and login
- User profile page
- Order history
- Wishlist
- Book recommendations based on purchased categories

### Blog
- Blog post listing
- Blog categories
- Blog detail page
- Comment system with admin approval
- Staff-only post creation

### Admin & Inventory
- Customized Django admin
- Product, order, review, banner and comment management
- Inventory report for low-stock books
- Low-stock email notification system

### API / Serialization
- DRF serializers for books, customers, orders and order items

### Testing
- Tests for forms
- Tests for models
- Tests for views
- Tests for URLs

### Deployment
- Dockerfile
- docker-compose for development
- docker-compose production setup
- PostgreSQL service
- Gunicorn
- Nginx
- Static and media volume handling

---

## Project Structure

```text
Smart_Inventory_Store/
├── Smart_Inventory_Store/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── store/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   ├── utils.py
│   ├── signals.py
│   ├── serializers.py
│   └── tests/
├── static/
├── templates/
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
└── requirements.txt


Installation
1. Clone the repository
git clone https://github.com/EliArn99/Smart_Inventory_Store.git
cd Smart_Inventory_Store
2. Create .env file
DJANGO_ENV=dev
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=bookstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

LOW_STOCK_ALERT_EMAIL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
3. Start with Docker
docker-compose up --build
4. Apply migrations
docker-compose exec web python manage.py migrate
5. Create superuser
docker-compose exec web python manage.py createsuperuser
6. Open the app
Storefront: http://127.0.0.1:8000/store/
Admin:      http://127.0.0.1:8000/admin/
Running Tests
docker-compose exec web python manage.py test
Environment Modes

The project uses separated Django settings:

settings/base.py
settings/dev.py
settings/prod.py

Set the active environment with:

DJANGO_ENV=dev

or:

DJANGO_ENV=prod
Screenshots
Storefront

Cart

Checkout

Admin Inventory

What I Learned
Structuring a real Django project with separate settings
Working with PostgreSQL and Docker
Handling authenticated and guest carts
Using transactions for order processing
Reducing stock safely after checkout
Creating custom Django admin panels
Writing tests for forms, models, views and URLs
Using vanilla JavaScript modules with Django templates
Preparing a Django app for production deployment
License

This project is licensed under the MIT License.

Contact

Eli Arnautska

GitHub: EliArn99
