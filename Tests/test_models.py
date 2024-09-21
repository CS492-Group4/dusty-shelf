from unittest.mock import patch
import unittest
from books.models import Book

class TestBookModel(unittest.TestCase):

    @patch('pymongo.MongoClient')  # Mock the MongoClient
    def test_add_book(self, MockMongoClient):
        mock_client = MockMongoClient()
        mock_db = mock_client['DustyShelf']
        mock_collection = mock_db['books']

        mock_collection.insert_one.return_value.inserted_id = 'mocked_id'

        book = {"title": "Test Book", "author": "Test Author", "price": 12.99, "quantity": 10}
        result = mock_collection.insert_one(book)

        self.assertTrue(mock_collection.insert_one.called)
        self.assertEqual(result.inserted_id, 'mocked_id')
