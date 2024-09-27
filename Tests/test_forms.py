from django.test import TestCase 
from books.forms import BookForm

class TestBookForm(TestCase):
    def test_valid_data(self):
        form = BookForm({
            'title': 'Sample Book',
            'author': 'Author Name',
            'price': 10.99,
            'quantity': 5,
            'vendor_name': 'Sample Vendor'
        })
        print(form.errors)  # Print errors if form is invalid
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = BookForm({
            'title': '',
            'author': 'Author Name',
            'price': 'invalid_price',
            'quantity': 5,
            'vendor_name': 'Sample Vendor'
        })
        self.assertFalse(form.is_valid())
