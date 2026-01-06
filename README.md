# Coderr - Freelance Marketplace Platform

A Django-based marketplace platform that connects customers with freelancers for various services. Built with Django REST Framework for robust API functionality.

## Features

### User Management
- User registration and authentication
- Business and customer user types
- Profile management with user types

### Marketplace Functionality
- **Offers**: Business users can create service offers with multiple tiers (Basic, Standard, Premium)
- **Orders**: Customers can place orders for specific offer tiers
- **Reviews**: Customers can review completed services
- **Order Management**: Track order status (In Progress, Completed, Cancelled)

### API Endpoints
- Offer management with filtering and searching
- Order lifecycle management
- Review system
- Analytics and statistics

## Tech Stack

- **Backend**: Django 5.2, 6.0
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (development)
- **Authentication**: Django's built-in auth system
- **Image Handling**: Pillow for image uploads
- **Filtering**: Django Filter for advanced querying

## Installation

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DeveloperRucel07/coderr.git
   cd coderr
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`


## API Documentation

### Key Endpoints

#### Authentication
- `POST /api/registration/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `GET /api/profile/` - Get User Profile Detail
- `PATCH /api/profile/` - Update User Profile Detail
- `GET /api/profiles/business/` - List all business profile (all authenticated users)
- `GET /api/profiles/customer/` - Lisdt all customer profile (all authenticated users)


#### Offers
- `GET /api/offers/` - List all offers (public)
- `POST /api/offers/` - Create new offer (business users only)
- `GET /api/offers/{id}/` - Get offer details
- `PATCH /api/offers/{id}/` - Update offer (owner only)
- `DELETE /api/offers/{id}/` - Delete offer (owner only)
- `GET /api/offerdetails/{id}/` - Get offerdetail (all authenticated users)

#### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create new order (customers only)
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/` - Update order status (business users)
- `DELETE /api/orders/{id}/` - Delete Order (only admin or staff users)
- `GET /api/order-count/{business_user_id}/` - count the all in_progress Order for the user (all authenticated users)
- `GET /api/completed-order-count/{business_user_id}/` - count the all Completed Order for the user (all authenticated users)

#### Reviews
- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create new review (customers only)
- `PATCH /api/reviews/{id}/` -  Update a review (reviewer only)
- `DELETE /api/reviews/{id}` - Delete a review (reviewer only only)

#### Analytics
- `GET /api/base-info/` - Platform statistics (public)

## Models

### Profile
Reprensent a user Profile.

### Offer
Represents a service offer with multiple pricing tiers.

### OfferDetail
Contains specific details for each offer tier (Basic, Standard, Premium).

### Order
Represents a customer's purchase of a specific offer tier.

### Review
Customer reviews for completed services.

## Permissions

- **IsAdminOrStaff**: Admin and staff access
- **IsBusinessUserOrOwnerOrReadOnly**: Business users can create/modify their own offers
- **IsBusinessUserOrder**: Business users can manage their orders
- **IsCustomerReviewer**: Customers can create reviews
- **IsBusinessOrCustomerUser**: Users can access orders they're involved in
