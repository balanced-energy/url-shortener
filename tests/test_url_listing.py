import unittest
from unittest.mock import patch, Mock
from service.db_service import get_all_urls
from fastapi import HTTPException


class TestURLListing(unittest.TestCase):

    @patch('service.db_service.URLModel.scan')
    def test_listing_with_existing_urls(self, mock_scan):
        mock_scan.return_value = [Mock(short_url='short1', url='https://example1.com'),
                                  Mock(short_url='short2', url='https://example2.com')]
        result = get_all_urls()
        expected_result = [{"short_url": "short1", "original_url": "https://example1.com"},
                           {"short_url": "short2", "original_url": "https://example2.com"}]
        self.assertEqual(result, expected_result)

    @patch('service.db_service.URLModel.scan')
    def test_listing_with_no_urls(self, mock_scan):
        mock_scan.return_value = []
        result = get_all_urls()
        self.assertEqual(result, [])

    @patch('service.db_service.URLModel.scan')
    def test_listing_with_db_error(self, mock_scan):
        mock_scan.side_effect = ConnectionError("DB connection error")
        with self.assertRaises(HTTPException) as context:
            get_all_urls()
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "An error occurred: DB connection error")


# If this script is run directly, it will execute the tests.
if __name__ == '__main__':
    unittest.main()
