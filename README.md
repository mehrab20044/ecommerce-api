# 🛒 Shop API – Django REST Framework

A backend e-commerce API built with Django REST Framework, focusing on clean architecture and core e-commerce workflows.

---

## 🚀 Tech Stack

- Django 6.x
- Django REST Framework
- SQLite (Development)
- PostgreSQL (Ready for production)
- Docker (Basic setup)
- JWT Authentication (SimpleJWT / Djoser)
- Swagger (drf-yasg)

---

## 📦 Features

### 🔐 Authentication (Accounts)
- User registration & login
- JWT authentication
- Profile management
- Password management (if enabled)

---

### 🛍️ Catalog
- Product listing
- Category system
- Product detail endpoint
- Wishlist functionality

---

### 🛒 Cart System
- Add / update / delete cart items
- Clear cart
- User-based cart isolation
- Quantity aggregation

---

### 📦 Order System
- Checkout from cart
- Order creation with transaction safety
- Order items snapshot (product title, price at time of purchase)
- Order history per user

---

### 💳 Payment System
- Payment creation linked to order
- Payment verification endpoint
- Payment status handling:
  - pending
  - success
  - failed
- Order status update after payment

---

### ⭐ Review System
- Create / update / delete reviews
- User-based access control

---

## ⚙️ Architecture Overview

