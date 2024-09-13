from django.urls import path
from books import views
from django.contrib.auth import views as auth_views

urlpatterns = [
     path('dashboard/', views.user_dashboard, name='dashboard'),
    path('manage_inventory/', views.manage_inventory, name='manage_inventory'),
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/<str:book_id>/', views.edit_book, name='edit_book'),
    path('delete_book/<str:book_id>/', views.delete_book, name='delete_book'),
    path('search_books/', views.search_books, name='search_books'),
    path('register/', views.register_customer, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('create_admin/', views.create_admin, name='create_admin'),
]
print("books/urls.py is being loaded!")

