from django.urls import path
from books import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('add_book/', views.add_book, name='add_book'),
    path('search_books/', views.search_books, name='search_books'),
    path('register/', views.register_customer, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
]
print("books/urls.py is being loaded!")
