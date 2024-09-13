from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

#Registration Form
class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

#Books Form
class BookForm(forms.Form):
    title = forms.CharField(max_length=200, label='Book Title')
    author = forms.CharField(max_length=200, label='Author')
    price = forms.DecimalField(max_digits=6, decimal_places=2, label='Price')
    quantity = forms.IntegerField(min_value=1, label='Quantity')