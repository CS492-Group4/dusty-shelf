from django.http import HttpResponse
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]

# Function to add a book
def add_book(request):
    name = request.GET.get('name')
    author = request.GET.get('author')
    price = float(request.GET.get('price'))
    quantity = int(request.GET.get('quantity'))
    
    book = {
        "title": name,
        "author": author,
        "price": price,
        "quantity": quantity
    }
    result = books_collection.insert_one(book)
    return HttpResponse(f"Book added with ID: {result.inserted_id}")
