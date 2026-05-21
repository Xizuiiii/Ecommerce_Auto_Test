from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ApiError(RuntimeError):
    """Raised when the remote shop API returns an unexpected response."""


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str | None = None


class ShopApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: int = 30,
        verify_ssl: bool = True,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = session or requests.Session()
        self.tokens: AuthTokens | None = None
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Avoid accidentally routing public test APIs through a local corporate proxy.
        self.session.trust_env = False

    @property
    def token(self) -> str | None:
        return self.tokens.access_token if self.tokens else None

    def login(self, username: str, password: str) -> AuthTokens:
        response = self._request(
            "POST",
            "/auth/login",
            json={"username": username, "password": password, "expiresInMins": 30},
            authenticated=False,
        )
        data = self._json(response)

        # DummyJSON currently returns accessToken. Keep token as a fallback for older mocks.
        access_token = data.get("accessToken") or data.get("token")
        if not access_token:
            raise ApiError(f"Login response did not contain an access token: {data}")

        self.tokens = AuthTokens(
            access_token=access_token,
            refresh_token=data.get("refreshToken"),
        )
        return self.tokens

    def get_user_profile(self) -> dict[str, Any]:
        response = self._request("GET", "/auth/me")
        return self._json(response)

    def refresh_auth_session(self) -> AuthTokens:
        if not self.tokens or not self.tokens.refresh_token:
            raise ApiError("Login is required before refreshing the auth session.")

        response = self._request(
            "POST",
            "/auth/refresh",
            json={"refreshToken": self.tokens.refresh_token, "expiresInMins": 30},
            authenticated=False,
        )
        data = self._json(response)
        access_token = data.get("accessToken") or data.get("token")
        if not access_token:
            raise ApiError(f"Refresh response did not contain an access token: {data}")

        self.tokens = AuthTokens(
            access_token=access_token,
            refresh_token=data.get("refreshToken", self.tokens.refresh_token),
        )
        return self.tokens

    def add_to_cart(self, item_id: int, *, user_id: int = 1, quantity: int = 1) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/carts/add",
            json={
                "userId": user_id,
                "products": [{"id": item_id, "quantity": quantity}],
            },
        )
        return self._json(response)

    def get_cart_items(self, *, user_id: int = 1) -> dict[str, Any]:
        response = self._request("GET", f"/carts/user/{user_id}")
        return self._json(response)

    def _request(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        headers = dict(kwargs.pop("headers", {}))
        if authenticated:
            if not self.token:
                raise ApiError("Login is required before calling authenticated endpoints.")
            headers["Authorization"] = f"Bearer {self.token}"

        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs,
        )
        if response.status_code >= 400:
            raise ApiError(
                f"{method} {path} failed with {response.status_code}: {response.text}"
            )
        return response

    @staticmethod
    def _json(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise ApiError(f"Response was not JSON: {response.text}") from exc
        if not isinstance(data, dict):
            raise ApiError(f"Expected a JSON object, got: {data!r}")
        return data
