# Dusty Shelf Bookstore Management System

## Description
This is a Django-based application for managing bookstore inventory, sales, and customer orders. The system allows admins and employees to manage books, assign credits, and track customer purchases.

## Requirements
- Django==3.2
- pymongo==3.12.1
- djongo==1.3.6
- Virtual Environment

## Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dusty-shelf.git
   cd dusty-shelf

2. Install dependencies:
   pip install -r requirements.txt

3. Run migrations:
   python manage.py migrate

4. Run server:
   python manage.py runserver

5. Access Application:
   http://127.0.0.1:8000/

   Included users are:
	user: Customer1
	password: 1password1

	user: Employee1
	password: 1password1

	user: Admin1
	password: 1password1

	Superuser: Superuser
	password: 1password1

6. Running python manage.py test requires deleting the old testcustomer
   unless new user name is created for the test_views.py under
   #Test create customer
 