from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import unittest
from api.api_endpoints import app  # make sure to import your FastAPI app correctly
from pynamodb.exceptions import DoesNotExist

client = TestClient(app)


class TestRedirect(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_get_patcher = patch('api.api_handlers.URLModel.get')
        self.mock_get = self.mock_get_patcher.start()

    def tearDown(self):
        self.mock_get_patcher.stop()

    def test_redirect_success(self):
        mock_instance = Mock()
        mock_instance.url = "https://existing.url"
        self.mock_get.return_value = mock_instance

        # Set 'allow_redirects' to False to test the initial redirect response without following the redirect.
        response = self.client.get("/redirect/exists", allow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "https://existing.url")

    def test_redirect_not_found(self):
        self.mock_get.side_effect = DoesNotExist

        response = self.client.get("/redirect/doesnotexist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], f'No URL for "doesnotexist" found')

    def test_redirect_exception(self):
        self.mock_get.side_effect = Exception("Unexpected error")

        response = self.client.get("/redirect/someShortUrl")
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "An unexpected error occurred")