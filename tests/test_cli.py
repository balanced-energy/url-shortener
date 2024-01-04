import unittest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from utils.cli import app
from utils.constants import *


class TestCLICommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("utils.cli.save_token")
    @patch("utils.cli.load_token", return_value="test_token")
    @patch("httpx.post")
    def test_login_successful(self, mock_post, mock_load_token, mock_save_token):
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: {"access_token": "token"}
        )

        result = self.runner.invoke(
            app, ["login", "--username", "user", "--password", "pass"]
        )
        self.assertIn(CLI_LOGIN_SUCCESS, result.output)

    @patch("httpx.post")
    def test_login_failed(self, mock_post):
        mock_post.return_value = MagicMock(status_code=401)

        result = self.runner.invoke(
            app, ["login", "--username", "user", "--password", "wrongpass"]
        )
        self.assertIn(CLI_INVALID_LOGIN, result.output)

    @patch("service.api_service.generate_short_url_id", return_value="shortened_id")
    @patch("utils.cli.load_token", return_value="test_token")
    @patch("httpx.post")
    def test_shorten_url_successful(
        self, mock_post, mock_load_token, mock_generate_short_url_id
    ):
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: {"short_url": "shortened_url"}
        )

        result = self.runner.invoke(app, ["shorten", "--url", "http://longurl.com"])
        expected_output = CLI_SHORT_URL_RESULT.format(short_url="shortened_url")
        self.assertIn(expected_output, result.output)

    @patch("utils.cli.is_admin", return_value=True)
    @patch("utils.cli.load_token", return_value="test_token")
    @patch("httpx.get")
    def test_list_urls(self, mock_get, mock_load_token, mock_is_admin):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [
                {"short_url": "short", "original_url": "http://original.com"}
            ],
        )

        result = self.runner.invoke(app, ["list-urls"])
        self.assertIn(
            "Short URL: short -> Original URL: http://original.com", result.output
        )

    @patch("utils.cli.is_admin", return_value=False)
    @patch("utils.cli.load_token", return_value="test_token")
    def test_list_urls_as_non_admin(self, mock_load_token, mock_is_admin):
        result = self.runner.invoke(app, ["list with -urls"])
        self.assertIn(CLI_ADMIN_ACCESS, result.output)

    @patch("httpx.get")
    def test_get_original_url(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200, headers={"X-Original-URL": "http://original.com"}
        )

        result = self.runner.invoke(app, ["get-original-url", "shorturl"])
        self.assertIn("http://original.com", result.output)


if __name__ == "__main__":
    unittest.main()
