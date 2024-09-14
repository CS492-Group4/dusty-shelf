from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal
from bson import ObjectId
from bson import Decimal128

# Book model for storing book information
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.title

#models for Users
class UserProfile(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=lambda: str(ObjectId()))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.CharField(max_length=100, default=str(Decimal128('0.00')))
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    personal_library = models.ManyToManyField(Book, blank=True)

    def __str__(self):
        return f"{self.user.username} - Admin: {self.is_admin} - Employee: {self.is_employee} - Credit: {self.credit}"
    

#models for receipts.
class Receipt(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=lambda: str(ObjectId()))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_title = models.CharField(max_length=200)
    book_author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.book_title} - {self.purchase_date}"