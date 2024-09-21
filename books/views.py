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
from bson import Decimal128
from .models import Receipt
from django.forms import formset_factory
from .forms import BulkOrderReceiptForm, BulkOrderForm
from .models import BulkOrderReceipt
from .models import BulkOrderItem

# MongoDB connection
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]
personal_library_collection = db["personal_library"]

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

# Role-based Profile view backend
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Dashboard
#@login_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'credit': '0.00'})
    
    context = {
        'is_admin': user_profile.is_admin,
        'is_employee': user_profile.is_employee,
        'credit': user_profile.credit,
        'can_manage_inventory': user_profile.is_admin or user_profile.is_employee,
        'can_order_books': user_profile.is_admin or user_profile.is_employee,
        'show_bulk_order_receipts': user_profile.is_admin,
    }
    
    return render(request, 'dashboard.html', context)



# Manage Inventory View
#@login_required
#@user_passes_test(is_admin_or_employee)
def manage_inventory(request):
    # Fetch all books from MongoDB
    books = list(books_collection.find())

    for book in books:
        book['id'] = str(book['_id'])

    return render(request, 'manage_inventory.html', {'books': books})

#Edit Book View
#@login_required
#@user_passes_test(is_admin_or_employee)
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
#@login_required
#@user_passes_test(is_admin_or_employee)
def delete_book(request, book_id):
    books_collection.delete_one({"_id": ObjectId(book_id)})
    return redirect('manage_inventory')

# Add book view page
#@login_required
#@user_passes_test(is_admin_or_employee)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            price = float(form.cleaned_data['price'])
            quantity = form.cleaned_data['quantity']
            vendor_name = form.cleaned_data['vendor_name']  # Get vendor name

            # Insert the book into MongoDB
            book = {
                "title": title,
                "author": author,
                "price": price,
                "quantity": quantity,
                "vendor_name": vendor_name
            }
            books_collection.insert_one(book)

            # Create a corresponding BulkOrderReceipt in the database
            bulk_order_receipt = BulkOrderReceipt.objects.create(
                vendor_name=vendor_name,
            )

            # Create a BulkOrderItem linked to the receipt
            BulkOrderItem.objects.create(
                bulk_order=bulk_order_receipt,
                title=title,
                author=author,
                price=Decimal(price),
                quantity=quantity
            )

            return redirect('manage_inventory')

    else:
        form = BookForm()

    return render(request, 'add_book.html', {'form': form})

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
    
    user_profile = UserProfile.objects.get(user=request.user)
    current_credit = user_profile.credit


    return render(request, 'view_books.html', {'books': books, 'current_credit': current_credit, 'search_term': search_term})

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
    
# Purchase Books    
#@login_required
def purchase_book(request, book_id):
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if book and user_profile:
        book_price = Decimal(str(book['price']))
        
        # Check if the user has enough credit
        if Decimal(user_profile.credit) >= book_price:
            # Deduct the price from user's credit
            user_profile.credit = str(Decimal(user_profile.credit) - book_price)
            user_profile.save()

            # Reduce the book quantity
            if book['quantity'] > 0:
                books_collection.update_one(
                    {"_id": ObjectId(book_id)},
                    {"$inc": {"quantity": -1}}
                )

                # Add the book to user's personal library
                personal_library_collection.insert_one({
                    "user_id": str(request.user.id),
                    "book_id": str(book['_id']),
                    "title": book['title'],
                    "author": book['author'],
                    "price": book['price']
                })

                # Create a receipt entry for the purchase
                Receipt.objects.create(
                    user=request.user,
                    book_title=book['title'],
                    book_author=book['author'],
                    price=book_price,
                    quantity=1
                )

                messages.success(request, "Purchase successful! Book added to your library.")
            else:
                messages.error(request, "Sorry, this book is out of stock.")
        else:
            messages.error(request, "You don't have enough credit to purchase this book.")
    
    return redirect('view_books')

# Customer Personal Library
#@login_required
def view_personal_library(request):
    user_id = str(request.user.id)
    personal_books = list(personal_library_collection.find({"user_id": user_id}))

    for book in personal_books:
        book['id'] = str(book['_id'])

    return render(request, 'view_personal_library.html', {'books': personal_books})

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

# Create an employee
#@login_required
#@user_passes_test(is_admin_or_employee)
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


# Create an admin
#@login_required
#@user_passes_test(is_admin)
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

#landing page Redirect
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, 'landing.html') 

#Custom-Login Redirect
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

#Assign Credit
#@login_required
#@user_passes_test(is_admin)
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

#User Search for Credit
from django.contrib.auth.models import User

#@login_required
#@user_passes_test(is_admin)  # Only admins can search users
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

#@login_required
#@user_passes_test(is_admin_or_employee)
def view_all_receipts(request):
    receipts = Receipt.objects.all().order_by('-purchase_date')
    return render(request, 'view_all_receipts.html', {'receipts': receipts})


# MongoDB connection
from pymongo import MongoClient
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]

# Bulk order view
#@login_required
#@user_passes_test(is_admin_or_employee)
def bulk_order_books(request):
    BulkOrderFormSet = formset_factory(BulkOrderForm, extra=5)

    if request.method == 'POST':
        formset = BulkOrderFormSet(request.POST)
        receipt_form = BulkOrderReceiptForm(request.POST)

        if formset.is_valid() and receipt_form.is_valid():
            # Create a new bulk order receipt
            bulk_order_receipt = receipt_form.save()

            # Initialize total price
            total_price = Decimal('0.00')

            for form in formset:
                if form.cleaned_data:
                    title = form.cleaned_data['title']
                    author = form.cleaned_data['author']
                    price = Decimal(form.cleaned_data['price'])
                    quantity = form.cleaned_data['quantity']

                    # Create a BulkOrderItem linked to the receipt
                    BulkOrderItem.objects.create(
                        bulk_order=bulk_order_receipt,
                        title=title,
                        author=author,
                        price=price,
                        quantity=quantity
                    )

                    total_price += price * quantity

            bulk_order_receipt.total_price = total_price
            bulk_order_receipt.save()

            return redirect('manage_inventory')  # Redirect after adding books

    else:
        formset = BulkOrderFormSet()
        receipt_form = BulkOrderReceiptForm()

    return render(request, 'bulk_order_books.html', {'formset': formset, 'receipt_form': receipt_form})


# Bulk Order Receipts
#@login_required
#@user_passes_test(is_admin_or_employee)
def bulk_order_receipts_view(request):
    receipts = BulkOrderReceipt.objects.prefetch_related('items').order_by('-order_date').all()  # Fetch related items for each receipt
    
    receipt_data = []
    for receipt in receipts:
        # Calculate total price by summing price * quantity for each item
        total_price = sum(Decimal(item.price.to_decimal()) * item.quantity for item in receipt.items.all())
        receipt_data.append({
            'vendor_name': receipt.vendor_name,
            'order_date': receipt.order_date,
            'items': receipt.items.all(),
            'total_price': total_price
        })
    
    return render(request, 'bulk_order_receipts.html', {'receipt_data': receipt_data})

