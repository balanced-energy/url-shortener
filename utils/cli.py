import typer
import httpx
import os
import pathlib
import stat
from utils.constants import *
from utils.logger_config import logger
from service.api_service import generate_short_url_id

app = typer.Typer()


# CLI commands
@app.command()
def login(
    username: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True, hide_input=True),
):
    form_data = {"username": username, "password": password}
    try:
        response = httpx.post(f"{SERVER_URL_PORT}/token", data=form_data)
        logger.info(CLI_LOGIN_RESPONSE.format(response_code=response.status_code))

        if response.status_code == 200:
            token = response.json()["access_token"]
            save_token(token)
            typer.echo(CLI_LOGIN_SUCCESS)
        elif response.status_code == 401:
            typer.echo(CLI_INVALID_LOGIN, err=True)
        else:
            typer.echo(CLI_LOGIN_FAILED, err=True)
    except Exception as e:
        typer.echo(CLI_ERROR.format(error=e), err=True)


@app.command()
def shorten(url: str = typer.Option(...), short_url: str = typer.Option(None)):
    token = load_token()
    # Check user is logged in
    if not token:
        typer.echo(CLI_NOT_LOGGED_IN, err=True)
        raise typer.Exit()
    # Create custom URL if one isn't provided
    if not short_url:
        short_url = generate_short_url_id()

    # Prepare payload
    json_data = {"url": url, "short_url": short_url}
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.post(
            f"{SERVER_URL_PORT}/shorten_url", json=json_data, headers=headers
        )
        if response.status_code == 200:
            short_url = response.json()["short_url"]
            typer.echo(CLI_SHORT_URL_RESULT.format(short_url=short_url))
        else:
            typer.echo(response.text, err=True)
    except httpx.HTTPError as e:
        typer.echo(CLI_ERROR.format(error=e), err=True)
    except Exception as e:
        typer.echo(CLI_ERROR.format(error=e), err=True)


@app.command()
def list_urls():
    if not is_admin():
        typer.echo(CLI_ADMIN_ACCESS)
        raise typer.Exit()

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = httpx.get(f"{SERVER_URL_PORT}/list_urls", headers=headers)
        response.raise_for_status()
        urls = response.json()

        if urls:
            for url in urls:
                typer.echo(
                    f"Short URL: {url['short_url']} -> Original URL: {url['original_url']}"
                )
        else:
            typer.echo(CLI_NO_URLS)
    except httpx.HTTPError as e:
        typer.echo(CLI_ERROR.format(error=e))
    except Exception as e:
        typer.echo(CLI_ERROR.format(error=e))


@app.command()
def get_original_url(short_url: str = typer.Argument(...)):
    try:
        response = httpx.get(f"{SERVER_URL_PORT}/redirect/{short_url}")
        original_url = response.headers.get("X-Original-URL")

        if original_url:
            typer.echo(original_url)
        else:
            typer.echo(CLI_NO_ORIGINAL_URL)
    except httpx.HTTPError as e:
        typer.echo(CLI_ERROR.format(error=e))
    except Exception as e:
        typer.echo(CLI_ERROR.format(error=e))


# Token handling
def save_token(token: str):
    token_file_path = pathlib.Path.home() / ".url_shortener_token"
    with open(token_file_path, "w") as token_file:
        token_file.write(token)
    os.chmod(token_file_path, stat.S_IRUSR | stat.S_IWUSR)
    logger.info(CLI_TOKEN_SAVED)


def load_token():
    token_file_path = pathlib.Path.home() / ".url_shortener_token"
    try:
        with open(token_file_path, "r") as token_file:
            return token_file.read().strip()
    except FileNotFoundError:
        return None


# Check if the currently authenticated user is an admin.
def is_admin() -> bool:
    logger.info(ADMIN_STATUS_CHECK_LOG)
    token = load_token()
    if not token:
        logger.info(CLI_NOT_LOGGED_IN)
        return False

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.get(f"{SERVER_URL_PORT}/users/me", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        return user_data.get("is_admin", False)
    except httpx.HTTPError as e:
        logger.error(ADMIN_STATUS_CHECK_ERROR.format(error=e))
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(error=e))
    return False


if __name__ == "__main__":
    app()
