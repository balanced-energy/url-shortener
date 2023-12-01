import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from api.api_endpoints import app
from service.auth_service import UserInDB

client = TestClient(app)

# Mock user data
mock_user = UserInDB(
    user_id="testuser",
    username="testuser",
    url_limit=10,
    is_admin=False,
    hashed_password="hashedpassword",
    disabled=False,
)


class TestShortURL(unittest.TestCase):
    @patch("api.api_endpoints.get_current_user", return_value=mock_user)
    @patch(
        "service.api_service.create_generated_short_url",
        return_value={"short_url": "generatedShort"},
    )
    def test_without_collisions_no_short_url(self, mock_create_url, mock_user_auth):
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())

    @patch("api.api_endpoints.get_current_user", return_value=mock_user)
    @patch(
        "service.api_service.create_custom_short_url",
        return_value={"short_url": "customShort"},
    )
    def test_without_collisions_with_short_url(self, mock_create_url, mock_user_auth):
        response = client.post(
            "/shorten_url",
            json={"url": "https://example.com", "short_url": "customShort"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", response.json())
        self.assertEqual(response.json()["short_url"], "customShort")

    @patch("api.api_endpoints.get_current_user", return_value=mock_user)
    @patch(
        "service.api_service.create_custom_short_url",
        side_effect=HTTPException(
            status_code=409, detail="Short URL 'customShort' already exists."
        ),
    )
    def test_with_collision_with_short_url(self, mock_create_url, mock_user_auth):
        response = client.post(
            "/shorten_url",
            json={"url": "https://example.com", "short_url": "customShort"},
        )
        self.assertEqual(response.status_code, 409)

    @patch("api.api_endpoints.get_current_user", return_value=mock_user)
    @patch(
        "service.api_service.save_url",
        side_effect=HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="URL limit reached."
        ),
    )
    def test_url_limit_reached(self, mock_save_url, mock_user_auth):
        response = client.post("/shorten_url", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "URL limit reached.")

    @patch("api.api_endpoints.get_current_user", return_value=mock_user)
    def test_with_invalid_url(self, mock_user_auth):
        response = client.post("/shorten_url", json={"url": "invalid-url"})
        self.assertEqual(response.status_code, 422)

    def test_excessively_long_url(self):
        long_url = "https://example.com/" + "a" * 2050
        response = client.post("/shorten_url", json={"url": long_url})
        self.assertEqual(response.status_code, 422)
        errors = response.json()["detail"]
        self.assertTrue(any("characters or less" in error["msg"] for error in errors))


if __name__ == "__main__":
    unittest.main()
