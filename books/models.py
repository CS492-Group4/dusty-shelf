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

class UserProfile(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=lambda: str(ObjectId()))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Store credit as Decimal128 in MongoDB
    credit = models.CharField(max_length=100, default=str(Decimal128('0.00')))
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Admin: {self.is_admin} - Employee: {self.is_employee} - Credit: {self.credit}"
