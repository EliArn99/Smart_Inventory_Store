# 📚 Smart Inventory Store

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **A Production-Ready Full-Stack E-Commerce & Inventory Management System**

Smart Inventory Store is a feature-rich web application that combines an elegant customer storefront with powerful inventory management capabilities. Built with Django, PostgreSQL, Docker, and vanilla JavaScript.

**[Live Demo](#)** • **[Report Bug](#)** • **[Request Feature](#)**

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
- [📸 Screenshots](#-screenshots)
- [🧠 Lessons Learned](#-lessons-learned)
- [📄 License](#-license)
- [📫 Contact](#-contact)

---

## ✨ Features

### 🏪 Storefront
- 📄 Product listing with pagination
- 🔍 Full-text search by title, author, and description
- 🗂️ Category-based filtering
- 🎚️ Advanced filters (price range, author, publication year)
- 🔃 Multi-criteria sorting (name, price, rating, year)
- ⭐ Product detail page with user reviews & ratings

### 🛒 Cart & Orders
- 👤 Persistent cart for authenticated users
- 🍪 Guest cart support via cookies
- ➕/➖ Dynamic cart item management
- ✅ Real-time stock validation before checkout
- 📦 Automatic inventory reduction after successful orders
- 🏠 Shipping address management

### 👤 User Features
- 🔐 Secure registration and login system
- 👤 Personalized user profile
- 📜 Complete order history
- ❤️ Wishlist functionality
- 🎯 Smart recommendations based on purchase history

### 📝 Blog System
- 📰 Blog post listing with category filters
- 📄 Detailed blog post pages
- 💬 Comment system with admin moderation
- ✍️ Staff-only content creation

### 🛠️ Admin & Inventory
- 🧰 Fully customized Django admin panel
- 📊 Low-stock inventory reports
- 📧 Automated low-stock email alerts

### 🔌 API
- 📡 RESTful API with Django REST Framework
- 🔄 Serializers for books, customers, orders, and order items

### 🧪 Testing
- ✅ Comprehensive tests for forms
- ✅ Model validation tests
- ✅ View and URL routing tests

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python) ![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django) ![DRF](https://img.shields.io/badge/DRF-3.15-a30000?logo=django) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql) |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap) ![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?logo=javascript) |
| **Server** | ![Gunicorn](https://img.shields.io/badge/Gunicorn-21.2-499848?logo=gunicorn) ![Nginx](https://img.shields.io/badge/Nginx-1.24-009639?logo=nginx) |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker) ![Docker Compose](https://img.shields.io/badge/Compose-2.20-2496ED?logo=docker) |

---

## 📁 Project Structure

```bash
Smart_Inventory_Store/
├── Smart_Inventory_Store/          # Project configuration
│   ├── settings/
│   │   ├── base.py                 # Shared settings (DRY principle)
│   │   ├── dev.py                  # Development environment
│   │   └── prod.py                 # Production environment
│   ├── urls.py                     # Main URL configuration
│   └── wsgi.py                     # WSGI entry point
├── store/                          # Main application
│   ├── models.py                   # Database models
│   ├── views.py                    # Business logic
│   ├── forms.py                    # Form validation
│   ├── admin.py                    # Admin interface
│   ├── urls.py                     # App routing
│   ├── utils.py                    # Helper functions
│   ├── signals.py                  # Event handlers
│   ├── serializers.py              # DRF serializers
│   └── tests/                      # Unit tests
├── static/                         # Static assets (CSS, JS, images)
├── templates/                      # HTML templates
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Development setup
├── docker-compose.prod.yml         # Production setup
└── requirements.txt                # Python dependencies
