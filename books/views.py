from django.http import HttpResponse
from pymongo import MongoClient
from django.shortcuts import render

# MongoDB connection
client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
db = client["DustyShelf"]
books_collection = db["books"]

print("add_book view is being called!")


def add_book(request):
    # logic to add a book
    return HttpResponse("Book added successfully!")

# Add book view
#def add_book(request):
#    name = request.GET.get('name')
#    author = request.GET.get('author')
#    price = float(request.GET.get('price'))
#    quantity = int(request.GET.get('quantity'))


#    book = {
#        "title": name,
 #       "author": author,
#        "price": price,
#        "quantity": quantity
#    }
#    result = books_collection.insert_one(book)
 #   return HttpResponse(f"Book added with ID: {result.inserted_id}")

# Search books view
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
