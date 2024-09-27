from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from bson import ObjectId
from pymongo import MongoClient
from books.models import BulkOrderReceipt, BulkOrderItem
from djongo.base import DatabaseWrapper
from unittest import mock
from decimal import Decimal
from django.contrib.auth.models import User
from books.models import UserProfile 



class TestUserDashboardView(TestCase):

    def setUp(self):
         self.client.login(username='testadmin', password='testpass123')

#Test create customer
    def test_create_customer(self):
        form_data = {
            'username': 'testcustomer',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }

        response = self.client.post(reverse('register'), data=form_data)

        self.assertEqual(response.status_code, 302)

        user = User.objects.filter(username='testcustomer').first()
        self.assertIsNotNone(user)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual(user_profile.credit, '0.00')

    def test_create_customer_invalid_password(self):
        form_data = {
            'username': 'testcustomermismatch',
            'password1': 'testpass123',
            'password2': 'differentpass123',  # Mismatching passwords
        }

        response = self.client.post(reverse('register'), data=form_data)
        
        self.assertEqual(response.status_code, 200)  # The form should be re-rendered
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")


    @patch('books.views.books_collection.insert_one')  
    def test_add_book_view(self, mock_insert_one):
        form_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'price': '9.99',
            'quantity': '10',
            'vendor_name': 'Test Vendor' 
        }

        response = self.client.post(reverse('add_book'), data=form_data)
        
        print(response.content.decode())  
        
        self.assertEqual(response.status_code, 302)
        
        mock_insert_one.assert_called_once_with({
            'title': 'Test Book',
            'author': 'Test Author',
            'price': 9.99,
            'quantity': 10,
            'vendor_name': 'Test Vendor' 
        })


#class TestManageInventoryView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.close_patcher = mock.patch.object(DatabaseWrapper, 'close', return_value=None)
        cls.close_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.close_patcher.stop()
        super().tearDownClass()

    @patch('books.views.books_collection.find')
    def test_manage_inventory_view(self, mock_find):
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


#class TestDeleteBookView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.close_patcher = mock.patch.object(DatabaseWrapper, 'close', return_value=None)
        cls.close_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.close_patcher.stop()
        super().tearDownClass()

    @patch('books.views.books_collection.delete_one')
    def test_delete_book_view(self, mock_delete_one):
        book_id = ObjectId("64f4d9378f7f1e07e4e3a07b")

        response = self.client.post(reverse('delete_book', args=[str(book_id)]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_inventory'))

        mock_delete_one.assert_called_once_with({"_id": ObjectId(book_id)})


#class TestEditBookView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.close_patcher = mock.patch.object(DatabaseWrapper, 'close', return_value=None)
        cls.close_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.close_patcher.stop()
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.client = MongoClient("mongodb+srv://mongodbstudent1:t4aK6RZdC4QE3eM4@cluster0.6cclx.mongodb.net/")
        cls.db = cls.client["DustyShelf"]
        cls.books_collection = cls.db["books"]
        
        cls.book = {
            "_id": ObjectId(),
            "title": "Test Book",
            "author": "Test Author",
            "price": 10.00,
            "quantity": 5
        }
        cls.books_collection.insert_one(cls.book)
    
    def test_edit_book_view_get(self):
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
            'quantity': 10,
            'vendor_name': 'Updated Vendor'
        }
        response = self.client.post(reverse('edit_book', kwargs={'book_id': str(self.book['_id'])}), data=form_data)
        self.assertEqual(response.status_code, 302) 

        updated_book = self.books_collection.find_one({"_id": self.book['_id']})
        self.assertEqual(updated_book['title'], 'Updated Book Title')
        self.assertEqual(updated_book['author'], 'Updated Author')
        self.assertEqual(updated_book['price'], 12.99)
        self.assertEqual(updated_book['quantity'], 10)




#class TestBulkOrderBooksView(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.close_patcher = mock.patch.object(DatabaseWrapper, 'close', return_value=None)
        cls.close_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.close_patcher.stop()
        super().tearDownClass()

    def test_bulk_order_books_view(self):
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
            'vendor_name': 'Test Vendor'
        }

        response = self.client.post(reverse('bulk_order_books'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_inventory'))

        receipt = BulkOrderReceipt.objects.filter(vendor_name='Test Vendor').latest('id')

        self.assertEqual(receipt.vendor_name, 'Test Vendor')

        items = BulkOrderItem.objects.filter(bulk_order=receipt)
        self.assertEqual(items.count(), 2)

        first_item = items[0]
        self.assertEqual(first_item.title, 'Test Book 1')
        self.assertEqual(first_item.author, 'Test Author 1')
        self.assertEqual(first_item.price.to_decimal(), Decimal('10.99'))
        self.assertEqual(first_item.quantity, 5)

        second_item = items[1]
        self.assertEqual(second_item.title, 'Test Book 2')
        self.assertEqual(second_item.author, 'Test Author 2')
        self.assertEqual(second_item.price.to_decimal(), Decimal('12.99'))
        self.assertEqual(second_item.quantity, 3)

#Bulk order missing field
def test_bulk_order_books_view_missing_fields(self):
    form_data = {
        'form-TOTAL_FORMS': '3',
        'form-INITIAL_FORMS': '0',
        'form-MIN_NUM_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-title': '',
        'form-0-author': '',
        'form-0-price': '',
        'form-0-quantity': '',
        'vendor_name': 'Test Vendor'
    }

    response = self.client.post(reverse('bulk_order_books'), data=form_data)
    self.assertEqual(response.status_code, 200) 
    self.assertFormError(response, 'formset', 'form-0-title', "This field is required.")