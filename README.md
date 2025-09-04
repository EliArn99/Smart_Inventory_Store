# Smart Inventory Store 🛒  
Ефективна платформа за управление на онлайн магазин с вграден склад.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)  
![Django](https://img.shields.io/badge/Django-4.x-green?logo=django&logoColor=white)  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue?logo=postgresql&logoColor=white)  
![Docker](https://img.shields.io/badge/Docker-Compose-informational?logo=docker&logoColor=white)  
![License](https://img.shields.io/badge/License-MIT-yellow?logo=open-source-initiative&logoColor=white)  

---

## 📑 Table of Contents
- [About the Project](#-about-the-project)
- [Built With](#-built-with)
- [Features](#-features)
- [Demo](#-demo)
- [Getting Started](#-getting-started)
  - [Prerequisites](#-prerequisites)
  - [Installation](#-installation)
- [Usage](#-usage)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
- [Acknowledgments](#-acknowledgments)

---

## 📌 About the Project
**Smart Inventory Store** е Django-базирана уеб платформа за управление на онлайн магазин със складова система.  

🔹 Управление на продукти и наличности  
🔹 Следене и обработка на поръчки  
🔹 Управление на доставчици  
🔹 Онлайн магазин за клиенти  

---

## 🛠 Built With
- [Python 3.9+](https://www.python.org/)  
- [Django 4.x](https://www.djangoproject.com/)  
- [Django REST Framework](https://www.django-rest-framework.org/)  
- [PostgreSQL](https://www.postgresql.org/)  
- [Bootstrap](https://getbootstrap.com/)  
- [Docker & Docker Compose](https://www.docker.com/)  

---

## 🌟 Features
- 🛍 **Онлайн магазин** – Продукти, количка, поръчки  
- ⚙️ **Административен панел** – Управление на продукти, наличности, поръчки и доставчици  
- 📦 **Интелигентно проследяване на наличностите** – Автоматично обновяване и предупреждения  
- 📑 **Управление на поръчки** – Преглед, обработка и филтриране  
- 🚚 **Модул за доставчици** – Регистрация и управление на доставчици  
- 🔐 **Сигурна автентикация** – Разделение на права за клиенти и администратори  

---

## 🖼 Demo
Преглед на публичната част и административния панел:  

- 🌐 Публичен магазин  
- 🔧 Административен панел  

*(тук можеш да добавиш **screenshots** или **gif demo**)*

---

## 🚀 Getting Started
Следвайте стъпките, за да стартирате проекта локално:

### ✅ Prerequisites
- Python 3.9+  
- pip  
- PostgreSQL  
- Git  
- Docker & Docker Compose  

### ⚙️ Installation
1. **Клонирай хранилището**
   ```bash
   git clone https://github.com/EliArn99/Smart_Inventory_Store.git
   cd Smart_Inventory_Store

2. **Създай .env файл**
Копирай .env.example и го преименувай на .env.
Попълни необходимата информация за базата данни.

3. **Стартирай контейнерите**
docker-compose up --build -d
