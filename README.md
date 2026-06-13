# E-Commerce-Project

A Django REST Framework based API to manage products, cart, orders, reviews and warehouse inventory with role-based access control for Customer, Vendor, Staff & Admin.

In E-Commerce API (Application Programming Interface) there are six APPs :

- **1) Authentication** :-
    Handles signup, login and JWT (JSON Web Token) token refresh for all users. Also manages user addresses and role switching between customer and vendor.

- **2) Product** :-
    Manages product and category list and detail. Vendor can add or update their own products, admin manages categories. Supports filtering, searching, ordering and Redis-based response caching.

- **3) Cart** :-
    Allows customer to add, update and remove products from their cart. Admin can also view any customer's cart.

- **4) Order** :-
    Handles order preview, placement, item cancellation and status updates. Supports coupon-based discounts. Vendor can update their own order item status, Admin can update overall order status.

- **5) Review** :-
    Allows customers to review products they have received (delivered orders only). Supports listing, updating and deleting reviews. Admin can also delete any review.

- **6) Warehouse** :-
    Manages warehouses, inventory and stock movements. Admin can create warehouses and assign staff. Assigned staff and admin can add/remove stock and view inventory and stock history.

**Tech Stack** — Django, DRF, MySQL, Celery, Redis, JWT (JSON Web Token).

---

## API Endpoints

### Authentication

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| POST | `/auth/register/` | Register a new user | Public |
| POST | `/auth/login/` | Login and get JWT tokens | Public |
| POST | `/auth/refresh/token/` | Refresh access token | Public |
| POST | `/auth/switch-role/` | Switch role (customer <-> vendor) | Authenticated |
| GET | `/auth/addresses/` | List user addresses | Customer |
| POST | `/auth/addresses/` | Add a new address | Customer |
| GET | `/auth/address/<id>/` | Get address detail | Customer |
| PUT | `/auth/address/<id>/` | Update an address | Customer |
| DELETE | `/auth/address/<id>/` | Delete an address | Customer |

### Products

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/products/` | List all products (filter, search, order) | Authenticated |
| POST | `/products/` | Add a new product | Vendor, Admin |
| GET | `/products/<id>/` | Get product detail with ratings | Authenticated |
| PUT | `/products/<id>/` | Update a product | Vendor (own), Admin |
| DELETE | `/products/<id>/` | Delete a product | Vendor (own), Admin |
| GET | `/products/categories/` | List all categories | Authenticated |
| POST | `/products/categories/` | Add a category | Admin |
| GET | `/products/categories/<id>/` | Get category detail | Authenticated |
| PUT | `/products/categories/<id>/` | Update a category | Admin |
| DELETE | `/products/categories/<id>/` | Delete a category | Admin |

> **Query Params for `GET /products/`:** `scope=mine`, `category`, `vendor`, `search`, `min_price`, `max_price`, `ordering` (`price`, `-price`, `created_at`, `-created_at`)

### Cart

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/carts/admin/users/<user_id>/cart/` | View any customer's cart | Admin |
| GET | `/carts/cart/` | View own cart items | Customer |
| POST | `/carts/cart/add/` | Add product to cart | Customer |
| GET | `/carts/cart/<id>/` | Get cart item detail | Customer |
| PUT | `/carts/cart/<id>/` | Update item quantity | Customer |
| DELETE | `/carts/cart/<id>/remove/` | Remove item from cart | Customer |

### Orders

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/orders/preview/` | Preview order pricing with coupon | Customer |
| POST | `/orders/place/` | Place a new order | Customer |
| GET | `/orders/` | List all orders | Customer, Vendor, Admin |
| GET | `/orders/<id>/` | Get order detail | Customer, Vendor, Admin |
| PATCH | `/orders/<id>/status/` | Update overall order status | Admin |
| PATCH | `/orders/item/<id>/status/` | Update order item status | Vendor (own items) |
| PATCH | `/orders/cancel-order-item/<id>/` | Cancel an order item | Customer |

> **Query Params for `GET /orders/preview/`:** `cart_item_ids` (comma-separated), `coupon`

### Reviews

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| GET | `/reviews/product/<id>/reviews/` | List reviews for a product | Authenticated |
| POST | `/reviews/product/<id>/reviews/` | Add a review (delivered orders only) | Customer |
| GET | `/reviews/<id>/` | Get review detail | Authenticated |
| PUT | `/reviews/<id>/` | Update a review | Review Owner |
| DELETE | `/reviews/<id>/` | Delete a review | Review Owner, Admin |

### Warehouse

| Method | URL | Description | Access |
|--------|-----|-------------|--------|
| POST | `/warehouses/assignment/` | Assign staff to a warehouse | Admin |
| GET | `/warehouses/` | List all warehouses | Admin |
| POST | `/warehouses/` | Create a warehouse | Admin |
| GET | `/warehouses/<id>/` | Get warehouse detail | Admin |
| PATCH | `/warehouses/<id>/` | Update a warehouse | Admin |
| DELETE | `/warehouses/<id>/` | Delete a warehouse | Admin |
| GET | `/warehouses/inventories/` | List all inventory | Admin, Assigned Staff |
| GET | `/warehouses/inventory/<id>/` | Get inventory detail | Admin, Assigned Staff |
| DELETE | `/warehouses/inventory/<id>/` | Delete an inventory record | Admin |
| GET | `/warehouses/<id>/inventory/` | List inventory of a warehouse | Admin, Assigned Staff |
| GET | `/warehouses/stock-movements/` | List all stock movements | Admin, Assigned Staff |
| GET | `/warehouses/stock-movements/<id>/` | Get stock movement detail | Admin, Assigned Staff |
| GET | `/warehouses/<id>/stock-movements/` | Stock movement history of a warehouse | Admin, Assigned Staff |
| POST | `/warehouses/<id>/inventory/add-stock/` | Add stock to warehouse | Admin, Assigned Staff |
| POST | `/warehouses/<id>/inventory/remove-stock/` | Remove stock from warehouse | Admin, Assigned Staff |

---


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

6. **Start celery worker** (Separate Terminal)
 ```
    celery -A ECommerce worker -l info --pool=solo
 ```




