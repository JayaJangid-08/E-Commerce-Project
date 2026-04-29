# E-Commerce-Project

A Django REST Framework based API to manage products, cart and orders with role-based access control for Customer, Vendor & Admin.

In E-Commerce API (Application Programming Interface) there are four APPs :

- **1) Authentication** :-
    Handles signup, login and JWT (JSON Web Token) token refresh for all users.

- **2) Product** :-
    Manages Product and category list and Detail. Vendor can add os update their own products, admin manages categories.

- **3) Cart** :-
    Allows user to add, update and remove products from their cart.

- **4) Order** :-
    Handles order placement, cancellation and status update. Vendor can update their own order product, Admin can update overall status.

**Tech Stack** — Django, DRF, MySQL, Celery, Redis, JWT (JSON Web Token).

---

## API Endpoints

### Authentication

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| POST | `/auth/signup/` | Register a new user | Public |
| POST | `/auth/login/` | Login and get JWT tokens | Public |
| POST | `/auth/refresh/token/` | Refresh access token | Public |

### Products

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/products/` | List all products | Authenticated |
| POST | `/products/` | Add a new product | Vendor, Admin |
| GET | `/products/<id>/` | Get product detail | Authenticated |
| PUT | `/products/<id>/` | Update a product | Vendor, Admin |
| DELETE | `/products/<id>/` | Delete a product | Vendor, Admin |
| GET | `/products/category/` | List all categories | Authenticated |
| POST | `/products/category/` | Add a category | Admin |
| PUT | `/products/category/<id>/` | Update a category | Admin |
| DELETE | `/products/category/<id>/` | Delete a category | Admin |

### Cart

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/carts/cart/` | View cart items | Customer |
| POST | `/carts/cart/add/` | Add product to cart | Customer |
| GET | `/carts/cart/<id>/` | Get cart item detail | Customer |
| PUT | `/carts/cart/<id>/` | Update item quantity | Customer |
| DELETE | `/carts/cart/<id>/remove/` | Remove item from cart | Customer |

### Orders

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/orders/` | List all orders | Customer, Admin |
| POST | `/orders/place/` | Place a new order | Customer |
| GET | `/orders/<id>/` | Get order detail | Customer, Vendor, Admin |
| PUT | `/orders/<id>/cancel/` | Cancel an order | Customer |
| PUT | `/orders/<id>/status/` | Update order status | Admin |
| PUT | `/orders/item/<id>/status/` | Update order item status | Vendor |


## Setup Instructions

### Prerequisites
- Python 3.x
- MySQL
- Redis (Memurai for Windows)

### Installation

1. **Clone the Repository**
 ```bash
    git clone https://github.com/JayaJangid-08/E-Commerce-Project.git
    cd E-Commerce-Project
 ```

2. **Install Dependencies**
 ```bash
    pip install django djangorestframework djangorestframework-simplejwt django-environ mysqlclient celery redis
 ```

3. **Create `.env` file** in root directory and add:
 ```
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=3306
    EMAIL_HOST_USER=your@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
 ```

4. **Run Migrations**
 ```bash
    python manage.py makemigrations
    python manage.py migrate
 ```

5. **Start the Server**
 ```bash
    python manage.py runserver
 ```

6. **Start celery worker** (separate terminal)
 ```
    celery -A ECommerce worker -l info --pool=solo
 ```




