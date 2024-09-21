from books.forms import BookForm
from django.test import TestCase

class TestBookForm(TestCase):

    def test_valid_data(self):
        form = BookForm({
            'title': 'Sample Book',
            'author': 'Author Name',
            'price': 10.99,
            'quantity': 5,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = BookForm({
            'title': '',
            'author': 'Author Name',
            'price': 'invalid_price',
            'quantity': 5,
        })
        self.assertFalse(form.is_valid())
