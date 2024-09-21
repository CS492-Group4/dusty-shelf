from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from bson import ObjectId
from pymongo import MongoClient





class TestBookView(TestCase):

    @patch('books.views.books_collection.insert_one')  # Mock the MongoDB collection insert
    def test_add_book_view(self, mock_insert_one):
        form_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'price': '9.99',
            'quantity': '10'
        }

        response = self.client.post(reverse('add_book'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_inventory'))

        mock_insert_one.assert_called_once_with({
            'title': 'Test Book',
            'author': 'Test Author',
            'price': 9.99,
            'quantity': 10
        })

class TestManageInventoryView(TestCase):
    
    @patch('books.views.books_collection.find')
    def test_manage_inventory_view(self, mock_find):
        # Setup mock data
        mock_books = [
            {"_id": 1, "title": "Book 1", "author": "Author 1", "price": 10.99, "quantity": 5},
            {"_id": 2, "title": "Book 2", "author": "Author 2", "price": 12.99, "quantity": 3},
        ]
        mock_find.return_value = mock_books
        
        response = self.client.get(reverse('manage_inventory'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'manage_inventory.html')

        self.assertIn('books', response.context)
        self.assertEqual(len(response.context['books']), 2)

        self.assertEqual(response.context['books'][0]['title'], 'Book 1')
        self.assertEqual(response.context['books'][1]['title'], 'Book 2')



class TestDeleteBookView(TestCase):

    @patch('books.views.books_collection.delete_one')
    def test_delete_book_view(self, mock_delete_one):
        book_id = ObjectId("64f4d9378f7f1e07e4e3a07b")

        response = self.client.post(reverse('delete_book', args=[str(book_id)]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_inventory'))

        mock_delete_one.assert_called_once_with({"_id": ObjectId(book_id)})

class TestEditBookView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup MongoDB connection and test data
        cls.client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
        cls.db = cls.client["DustyShelf"]
        cls.books_collection = cls.db["books"]
        
        # Insert a test book
        cls.book = {
            "_id": ObjectId(),
            "title": "Test Book",
            "author": "Test Author",
            "price": 10.00,
            "quantity": 5
        }
        cls.books_collection.insert_one(cls.book)
    
    def test_edit_book_view_get(self):
        # Test GET request to render the edit book form
        response = self.client.get(reverse('edit_book', kwargs={'book_id': str(self.book['_id'])}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Test Author')
        self.assertContains(response, 10.00)
        self.assertContains(response, 5)

    def test_edit_book_view_post(self):
        form_data = {
            'title': 'Updated Book Title',
            'author': 'Updated Author',
            'price': 12.99,
            'quantity': 10
        }
        response = self.client.post(reverse('edit_book', kwargs={'book_id': str(self.book['_id'])}), data=form_data)
        self.assertEqual(response.status_code, 302) 

        # Verify the book was updated in MongoDB
        updated_book = self.books_collection.find_one({"_id": self.book['_id']})
        self.assertEqual(updated_book['title'], 'Updated Book Title')
        self.assertEqual(updated_book['author'], 'Updated Author')
        self.assertEqual(updated_book['price'], 12.99)
        self.assertEqual(updated_book['quantity'], 10)

class TestBulkOrderBooksView(TestCase):

    @patch('books.views.books_collection.insert_one')  # Mock MongoDB insert
    def test_bulk_order_books_view(self, mock_insert_one):
        # Create test form data for multiple books
        form_data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'Test Book 1',
            'form-0-author': 'Test Author 1',
            'form-0-price': '10.99',
            'form-0-quantity': '5',
            'form-1-title': 'Test Book 2',
            'form-1-author': 'Test Author 2',
            'form-1-price': '12.99',
            'form-1-quantity': '3',
            'form-2-title': '',
            'form-2-author': '',
            'form-2-price': '',
            'form-2-quantity': '',
        }

        # Send a POST request to the bulk_order_books view
        response = self.client.post(reverse('bulk_order_books'), data=form_data)

        # Ensure the response redirects to the manage inventory page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_inventory'))

        # Check that insert_one was called twice (for 2 valid books)
        self.assertEqual(mock_insert_one.call_count, 2)

        # Verify the correct data was inserted for both books
        mock_insert_one.assert_any_call({
            'title': 'Test Book 1',
            'author': 'Test Author 1',
            'price': 10.99,
            'quantity': 5
        })

        mock_insert_one.assert_any_call({
            'title': 'Test Book 2',
            'author': 'Test Author 2',
            'price': 12.99,
            'quantity': 3
        })