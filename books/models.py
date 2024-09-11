from django.contrib.auth.models import User
from django.db import models

# Book model for storing book information
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Admin: {self.is_admin} - Employee: {self.is_employee} - Credit: {self.credit}"
