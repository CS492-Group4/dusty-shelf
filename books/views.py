from django.http import HttpResponse
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomerRegistrationForm
from .forms import BookForm
from django.shortcuts import get_object_or_404
from bson import ObjectId
from decimal import Decimal
from .models import UserProfile
from .forms import EmployeeCreationForm
from bson import Decimal128
from django.contrib.auth.decorators import user_passes_test

# MongoDB connection
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]

# Manage Inventory View
def manage_inventory(request):
    # Fetch all books from MongoDB
    books = list(books_collection.find())

    for book in books:
        book['id'] = str(book['_id'])

    return render(request, 'manage_inventory.html', {'books': books})


# Add book view page
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['title']
            author = form.cleaned_data['author']
            price = float(form.cleaned_data['price'])
            quantity = form.cleaned_data['quantity']

            book = {
                "title": name,
                "author": author,
                "price": price,
                "quantity": quantity
            }
            books_collection.insert_one(book)
            return redirect('dashboard')

    else:
        form = BookForm()

    return render(request, 'add_book.html', {'form': form})

# Search books view (Needs to be updated)
def search_books(request):
    search_term = request.GET.get('search_term')

    query = {"$or": [
        {"title": {"$regex": search_term, "$options": "i"}},
        {"author": {"$regex": search_term, "$options": "i"}}
    ]}
    
    results = books_collection.find(query)
    results_list = list(results)
    
    if len(results_list) == 0:
        return HttpResponse("No books found.")
    else:
        result_str = "Search Results:\n"
        for book in results_list:
            result_str += f"Title: {book['title']}, Author: {book['author']}, Price: ${book['price']}, Quantity: {book['quantity']}\n"
        return HttpResponse(result_str)
    
# Register Customer
def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            user_profile, created = UserProfile.objects.get_or_create(user=user, defaults={'credit': '0.00'})
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'register.html', {'form': form})


#Role-based Profile view backend
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'credit': '0.00'})
    
    context = {
        'is_admin': user_profile.is_admin,
        'is_employee': user_profile.is_employee,
        'credit': user_profile.credit,
        'can_manage_inventory': user_profile.is_admin or user_profile.is_employee,
    }
    
    return render(request, 'dashboard.html', context)


#Edit Book View
def edit_book(request, book_id):
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {
                    "title": form.cleaned_data['title'],
                    "author": form.cleaned_data['author'],
                    "price": form.cleaned_data['price'],
                    "quantity": form.cleaned_data['quantity']
                }}
            )
            return redirect('manage_inventory')
    else:
        form = BookForm(initial={
            'title': book['title'],
            'author': book['author'],
            'price': book['price'],
            'quantity': book['quantity'],
        })
    
    return render(request, 'edit_book.html', {'form': form, 'book_id': book_id})

#Delete Book View
def delete_book(request, book_id):
    books_collection.delete_one({"_id": ObjectId(book_id)})
    return redirect('manage_inventory')

# View to create an employee
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user, defaults={'is_employee': True, 'is_admin': False, 'credit': '0.00'})
            return redirect('dashboard')
    else:
        form = EmployeeCreationForm()

    return render(request, 'create_employee.html', {'form': form})


# View to create an admin
def create_admin(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user, defaults={'is_employee': False, 'is_admin': True, 'credit': '0.00'})
            return redirect('dashboard')
    else:
        form = EmployeeCreationForm()

    return render(request, 'create_admin.html', {'form': form})
