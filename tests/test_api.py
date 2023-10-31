import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.api_handlers import app

client = TestClient(app)


class TestShortURL(unittest.TestCase):

    @patch('service.db_service.save_url')
    def test_without_collisions_no_short_url(self, mock_save_url):
        mock_save_url.return_value = True
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    @patch('service.db_service.save_url')
    def test_with_collisions_no_short_url(self, mock_save_url):
        # Simulate a collision on the first call, then success on the second
        mock_save_url.side_effect = [False, True]
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    @patch('service.url_service.save_url')
    def test_without_collisions_with_short_url(self, mock_save_url):
        mock_save_url.return_value = True
        response = client.post("/shorten_url", json={"url": "https://example.com", "short_url": "customShort"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())
        self.assertEqual(response.json()["short_url"], "customShort")

    @patch('service.db_service.save_url')
    def test_with_collision_with_short_url(self, mock_save_url):
        mock_save_url.return_value = False
        response = client.post("/shorten_url", json={"url": "https://example.com", "short_url": "customShort"})
        self.assertEqual(response.status_code, 404)
        error_response = response.json()
        self.assertIn("detail", error_response)
        self.assertEqual(error_response["detail"], "Short URL 'customShort' already exists.")


if __name__ == "__main__":
    unittest.main()
