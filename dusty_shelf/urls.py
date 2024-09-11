from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Test view is working!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),
    path('test/', test_view), 
]
print("dusty_shelf/urls.py is being loaded!")
