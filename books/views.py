from django.http import HttpResponse
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import CustomerRegistrationForm
from .forms import BookForm
from bson import ObjectId
from .models import UserProfile
from .forms import EmployeeCreationForm
from django.contrib.auth.decorators import user_passes_test
from .forms import AdminCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from decimal import Decimal

# MongoDB connection
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]

# Employee/Admin lockout
def is_admin_or_employee(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile.is_admin or user_profile.is_employee
    except UserProfile.DoesNotExist:
        return False
    
# Admin lockout
def is_admin(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile.is_admin
    except UserProfile.DoesNotExist:
        return False

# Manage Inventory View
@login_required
@user_passes_test(is_admin_or_employee)
def manage_inventory(request):
    # Fetch all books from MongoDB
    books = list(books_collection.find())

    for book in books:
        book['id'] = str(book['_id'])

    return render(request, 'manage_inventory.html', {'books': books})


# Add book view page
@login_required
@user_passes_test(is_admin_or_employee)
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
            return redirect('manage_inventory')

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
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if not created:
                user_profile.credit = '0.00'
                user_profile.save()
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
@login_required
@user_passes_test(is_admin_or_employee)
def edit_book(request, book_id):
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            price = float(form.cleaned_data['price'])

            books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {
                    "title": form.cleaned_data['title'],
                    "author": form.cleaned_data['author'],
                    "price": price,
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
@login_required
@user_passes_test(is_admin_or_employee)
def delete_book(request, book_id):
    books_collection.delete_one({"_id": ObjectId(book_id)})
    return redirect('manage_inventory')

# View to create an employee
@login_required
@user_passes_test(is_admin_or_employee)
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                user_profile.is_employee = True
                user_profile.is_admin = False
                user_profile.credit = '0.00'
                user_profile.save()
            return redirect('dashboard')
    else:
        form = EmployeeCreationForm()

    return render(request, 'create_employee.html', {'form': form})


# View to create an admin
@login_required
@user_passes_test(is_admin)
def create_admin(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_superuser = True
            user.is_staff = True
            user.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                user_profile.is_employee = False
                user_profile.is_admin = True
                user_profile.credit = '0.00'
                user_profile.save()          
            login(request, user)
            return redirect('dashboard')
    else:
        form = AdminCreationForm()

    return render(request, 'create_admin.html', {'form': form})

#landing page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, 'landing.html') 

# View to display all books for customers
def view_books(request):
    search_term = request.GET.get('search_term', '')
    
    if search_term:
        # Search by title or author
        query = {"$or": [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"author": {"$regex": search_term, "$options": "i"}}
        ]}
        books = list(books_collection.find(query))
    else:
        # Fetch all books if no search term is entered
        books = list(books_collection.find())
    
    # Convert ObjectId to string for each book
    for book in books:
        book['id'] = str(book['_id'])

    return render(request, 'view_books.html', {'books': books, 'search_term': search_term})


#Custom-Login
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if the user is already logged in

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log in the user
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

#credit Administration
@login_required
@user_passes_test(is_admin)
def assign_credit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        try:
            # Get the amount to add from the form
            additional_credit = request.POST.get('credit')
            additional_credit = Decimal(additional_credit)
            
            # Add the new credit to the existing amount
            current_credit = Decimal(user_profile.credit)
            new_credit = current_credit + additional_credit
            
            # Update and save the profile with the new credit
            user_profile.credit = str(new_credit)
            user_profile.save()

            messages.success(request, f"Successfully added {additional_credit} credit to {user.username}. New balance: {new_credit}.")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Failed to add credit: {e}")

    return render(request, 'assign_credit.html', {'user': user, 'user_profile': user_profile})

#user Search option
from django.contrib.auth.models import User

@login_required
@user_passes_test(is_admin)  # Only admins can search users
def search_users(request):
    query = request.GET.get('query', '') 

    if query:
        users = User.objects.filter(username__icontains=query) | User.objects.filter(email__icontains=query)
    else:
        users = User.objects.all()

    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('selected_users') 
        credit_amount = request.POST.get('credit_amount', '0')

        for user_id in selected_user_ids:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_profile.credit = str(Decimal(user_profile.credit) + Decimal(credit_amount))
            user_profile.save()

        return redirect('search_users')

    return render(request, 'search_users.html', {'users': users, 'query': query})
