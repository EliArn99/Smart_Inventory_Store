# Smart Inventory Store 🛒

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)  
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

Efficient inventory, product, order & supplier management for retail stores — complete public storefront and admin dashboard.

---

## Table of Contents

- [About the project](#about-the-project)  
- [Built With](#built-with)  
- [Features](#features)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
- [Usage](#usage)  
- [Roadmap](#roadmap)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  
- [Acknowledgments](#acknowledgments)

---

## About the project

Smart Inventory Store е Django базирана уеб платформа за управление на онлайн магазин със вграден склад. Осигурява пълен публичен storefront за клиенти и администраторска част за управление на продукти, наличности, поръчки и доставчици.

---

## Built With

- Python 3.x  
- Django 4.x  
- PostgreSQL  
- HTML5, CSS3, JavaScript  
- Bootstrap  
- Docker & Docker Compose

---

## Features in development 🌟

- **Публичен онлайн магазин** – клиенти могат да разглеждат продукти, поставят количка и правят поръчка  
- **Административен панел** – за управление на продукти, складови наличности, поръчки и доставчици  
- **Inventory tracking** – автоматично обновяване на наличности при продажби и доставки  
- **Order management** – администратори могат да преглеждат и обработват поръчки  
- **Supplier management** – регистриране и преглед на доставчици, с контактна информация  
- **Dashboard с аналитични данни** – преглед на поръчки, топ продукти и наличности  
- **Responsive дизайн** – оптимизиран за мобилни и десктоп устройства  
- **Secure authentication** – логин, регистрация и администраторски права

---

## Getting Started

Следвай тези стъпки, за да стартираш проекта локално:

### Prerequisites

- Python 3.9+  
- pip  
- PostgreSQL  
- Git  
- Docker & Docker Compose

### Installation

1. **Clone the repo**
    ```bash
    git clone https://github.com/EliArn99/Smart-Inventory-Store.git
    cd Smart-Inventory-Store
    ```

2. **Създай база данни** и `.env` файл:
    ```env
    SECRET_KEY='your_secret_key'
    DEBUG=True
    DB_NAME='inventory_db'
    DB_USER='your_db_user'
    DB_PASSWORD='your_db_password'
    DB_HOST='localhost'
    DB_PORT='5432'
    ```

3. **Стартирай контейнерите**
    ```bash
    docker-compose up --build -d
    ```

4. **Прилагай миграции**
    ```bash
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    ```

5. **Създай суперпотребител**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

6. **Достъп до приложението**
    - Публична част: http://127.0.0.1:8000/  
    - Админ панел: http://127.0.0.1:8000/admin/

---

## Usage

- Клиенти могат да разглеждат продукти, добавят в количка и завършват поръчка  
- Администратори управляват продукти, наличности, поръчки и доставчици  
- Наличности се обновяват при доставка и продажба  
- Аналитичен дашборд с ключови метрики (ако е реализиран)

---

## Roadmap in development


---

## Contributing

1. Fork the repo  
2. Създай нов branch (`git checkout -b feature/awesome-feature`)  
3. Направи промени и commit (`git commit -m 'feat: Add awesome feature'`)  
4. Push to GitHub (`git push origin feature/awesome-feature`)  
5. Отвори Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

**Eli Arnautska**  
📧 eli_arnaytska@abv.bg  
🔗 [Smart Inventory Store GitHub Repo](https://github.com/EliArn99/Smart_Inventory_Store)

---

## Acknowledgments

- Django  
- PostgreSQL  
- Docker  
- Shields.io  
- Bootstrap  

---
