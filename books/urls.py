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
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('create_admin/', views.create_admin, name='create_admin'),
    path('', views.landing_page, name='landing_page'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='login.html'), name='login'),
    path('view_books/', views.view_books, name='view_books'),
    path('assign_credit/<int:user_id>/', views.assign_credit, name='assign_credit'),
    path('search_users/', views.search_users, name='search_users'),
    path('purchase_book/<str:book_id>/', views.purchase_book, name='purchase_book'),
    path('personal_library/', views.view_personal_library, name='personal_library'),
    path('view_all_receipts/', views.view_all_receipts, name='view_all_receipts'),
    path('bulk_order_books/', views.bulk_order_books, name='bulk_order_books'),
    path('bulk_order_receipts/', views.bulk_order_receipts_view, name='bulk_order_receipts'),

]
print("books/urls.py is being loaded!")

