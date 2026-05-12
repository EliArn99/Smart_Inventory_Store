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
