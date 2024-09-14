from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

#Customer Registration Form
class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

#Employee Registration
class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()

            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.is_employee = True  
            user_profile.is_admin = False 
            user_profile.save()
        return user

# Admin Registration
class AdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_superuser = True 
        user.is_staff = True
        if commit:
            user.save()

            user_profile, created = UserProfile.objects.get_or_create(user=user)

            user_profile.is_admin = True 
            user_profile.is_employee = False
            user_profile.save()
        return user

#Books Form
class BookForm(forms.Form):
    title = forms.CharField(max_length=200, label='Book Title')
    author = forms.CharField(max_length=200, label='Author')
    price = forms.DecimalField(max_digits=6, decimal_places=2, label='Price')
    quantity = forms.IntegerField(min_value=1, label='Quantity')

#Credit
class AssignCreditForm(forms.ModelForm):
    credit = forms.DecimalField(max_digits=10, decimal_places=2, label="Credit Amount")

    class Meta:
        model = UserProfile
        fields = ['credit']