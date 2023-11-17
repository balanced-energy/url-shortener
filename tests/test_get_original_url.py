import unittest
from unittest.mock import patch
from fastapi.exceptions import HTTPException
from service.db_service import get_original_url, URLModel
from pynamodb.exceptions import DoesNotExist


class TestGetOriginalURL(unittest.TestCase):
    @patch.object(URLModel, "get")
    def test_valid_retrieval(self, mock_get):
        # Mocking DB response for valid short URL
        expected_url = "https://example.com"
        mock_instance = URLModel()
        mock_instance.url = expected_url
        mock_get.return_value = mock_instance

        short_url = "validShort"
        result = get_original_url(short_url)

        self.assertEqual(result, expected_url)

    @patch.object(URLModel, "get")
    def test_invalid_retrieval(self, mock_get):
        # Mocking a DoesNotExist exception for a query with an invalid short URL
        mock_get.side_effect = DoesNotExist

        result = get_original_url("invalidShort")

        self.assertIsNone(result)

    @patch.object(URLModel, "get")
    def test_nonexistent_retrieval(self, mock_get):
        # Mocking a DoesNotExist exception for a query with a non-existent short URL
        mock_get.side_effect = DoesNotExist

        result = get_original_url("nonExistentShort")

        self.assertIsNone(result)

    @patch.object(URLModel, "get")
    def test_unexpected_exception(self, mock_get):
        # Mocking a different exception to simulate an unexpected error
        mock_get.side_effect = Exception("Unexpected error")

        with self.assertRaises(HTTPException) as context:
            get_original_url("someShortUrl")

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Unexpected error", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
