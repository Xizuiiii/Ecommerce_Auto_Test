import os

import pytest

try:
    from APITests.api_client import ShopApiClient
except ModuleNotFoundError:
    from api_client import ShopApiClient


def pytest_addoption(parser):
    parser.addoption(
        "--run-ui",
        action="store_true",
        default=False,
        help="Run Selenium UI tests in addition to API tests.",
    )


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("SHOP_API_BASE_URL", "https://dummyjson.com")


@pytest.fixture(scope="session")
def api_credentials() -> tuple[str, str]:
    username = os.getenv("SHOP_API_USERNAME", "emilys")
    password = os.getenv("SHOP_API_PASSWORD", "emilyspass")
    return username, password


@pytest.fixture()
def api_client(base_url: str, api_credentials: tuple[str, str]) -> ShopApiClient:
    client = ShopApiClient(base_url)
    client.login(*api_credentials)
    return client
