Smart Inventory Store 🛒
Ефективна платформа за управление на онлайн магазин с вграден склад.

Table of Contents
About the project

Built With

Features

Demo

Getting Started
  - Prerequisites
  - Installation

Usage

Roadmap

Contributing

License

Contact

Acknowledgments

About the project
Smart Inventory Store е Django базирана уеб платформа за управление на онлайн магазин със вграден склад. Тя предоставя цялостна система за управление на продукти, наличности, поръчки и доставчици, както и пълноценен онлайн магазин за клиенти.

Built With
Python 3.9+

Django 4.x

Django REST Framework

PostgreSQL

HTML5, CSS3, JavaScript

Bootstrap

Docker & Docker Compose

Features 🌟
Онлайн магазин – Позволява на клиентите да разглеждат продукти, да добавят артикули в количката и да завършват поръчки.

Административен панел – Интуитивен интерфейс за управление на продукти, складови наличности, поръчки и доставчици.

Интелигентно проследяване на наличностите – Автоматично обновяване на наличностите при всяка продажба и доставка, с предупреждения за изчерпващи се запаси.

Управление на поръчки – Администраторите могат лесно да преглеждат, обработват и филтрират поръчките.

Модул за доставчици – Система за регистриране и управление на информация за доставчиците.

Сигурна автентикация – Подсигурено влизане, регистрация и разделение на правата за клиенти и администратори.

Demo 🖼️
Поглед към публичната част и административния панел на приложението.

Публичен магазин
Административен панел
Getting Started
Следвайте тези стъпки, за да стартирате проекта локално:

Prerequisites
Python 3.9+

pip

PostgreSQL

Git

Docker & Docker Compose

Installation
Клонирай хранилището
    ```bash
git clone https://github.com/EliArn99/Smart_Inventory_Store.git
cd Smart_Inventory_Store

2.  **Създай `.env` файл**
    * Копирай `.env.example` и го преименувай на `.env`. Попълни необходимата информация за базата данни.

3.  **Стартирай контейнерите**
    ```bash
docker-compose up --build -d

_Тази команда изгражда и стартира всички необходими контейнери (уеб сървър и база данни) във фонов режим._

Приложи миграции
    ```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

    _Това създава таблиците в базата данни, необходими за работата на приложението._

5.  **Създай суперпотребител**
    ```bash
docker-compose exec web python manage.py createsuperuser

_Необходим е за достъп до административния панел._

Достъп до приложението
    - Публична част: http://127.0.0.1:8000/
    - Админ панел: http://127.0.0.1:8000/admin/

Usage
За клиенти: Разглеждайте продукти, добавяйте в количката, създавайте акаунт и правете поръчки.

За администратори: Използвайте админ панела за управление на продукти, наличности, поръчки и блог публикации.

Roadmap
Интеграция с платежни системи: Добавяне на Stripe или PayPal за обработка на реални плащания.

Подобрена аналитика: Изграждане на дашборд с по-подробни графики и отчети за продажбите.

Оценки и ревюта: Завършване на функционалността за писане на потребителски ревюта за книги.

Списъци с желания: Реализиране на пълна функционалност за запазване на желани книги.

Оптимизация на производителността: Кеширане на страници и заявки за по-бързо зареждане.

Contributing
Приносите са добре дошли! Моля, следвайте тези стъпки:

Fork the repo

Създай нов branch (git checkout -b feature/awesome-feature)

Направи промени и commit (git commit -m 'feat: Add awesome feature')

Push to GitHub (git push origin feature/awesome-feature)

Отвори Pull Request

License
Разпространява се под MIT License. За повече информация вижте файла LICENSE.

Contact
Eli Arnautska
📧 eli_arnaytska@abv.bg
🔗 Smart Inventory Store GitHub Repo

Acknowledgments
Django

PostgreSQL

Docker

Shields.io

Bootstrap
