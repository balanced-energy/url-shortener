import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.api_endpoints import app

client = TestClient(app)


class TestShortURL(unittest.TestCase):

    @patch('service.api_service.save_url')
    def test_without_collisions_no_short_url(self, mock_save_url):
        mock_save_url.return_value = True
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    @patch('service.api_service.save_url')
    def test_with_collisions_no_short_url(self, mock_save_url):
        # Simulate a collision on the first call, then success on the second
        mock_save_url.side_effect = [False, True]
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    @patch('service.api_service.save_url')
    def test_without_collisions_with_short_url(self, mock_save_url):
        mock_save_url.return_value = True
        response = client.post("/shorten_url", json={"url": "https://example.com", "short_url": "customShort"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())
        self.assertEqual(response.json()["short_url"], "customShort")

    @patch('service.api_service.save_url')
    def test_with_collision_with_short_url(self, mock_save_url):
        mock_save_url.return_value = False
        response = client.post("/shorten_url", json={"url": "https://example.com", "short_url": "customShort"})
        self.assertEqual(response.status_code, 404)
        error_response = response.json()
        self.assertIn("detail", error_response)
        self.assertEqual(error_response["detail"], "Short URL 'customShort' already exists.")

    @patch('service.api_service.save_url')
    def test_with_invalid_url(self, mock_save_url):
        # Provide an invalid URL format that fails Pydantic validation
        response = client.post("/shorten_url", json={"url": "invalid-url"})
        self.assertEqual(response.status_code, 422)

    def test_excessively_long_url(self):
        # Create an excessively long URL
        long_url = "https://example.com/" + "a" * 2050
        response = client.post("/shorten_url", json={"url": long_url})
        self.assertEqual(response.status_code, 422)
        # The actual error message is in the list under 'detail', so we need to navigate to it
        errors = response.json()['detail']
        self.assertTrue(any('characters or less' in error['msg'] for error in errors))


if __name__ == "__main__":
    unittest.main()
