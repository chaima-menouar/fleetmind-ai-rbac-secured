"""Supabase Auth adapter for viewer email verification and sign-in."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models.schemas import CurrentUser, UserRole


class SupabaseAuthError(ValueError):
    """Safe authentication error that may be returned to the API caller."""


def enabled() -> bool:
    return bool(os.getenv("SUPABASE_URL", "").strip() and os.getenv("SUPABASE_ANON_KEY", "").strip())


def _require_enabled() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    if not url or not key:
        raise SupabaseAuthError("Email verification is not configured yet.")
    return url, key


def _request(path: str, *, method: str = "POST", payload: dict | None = None, token: str | None = None) -> dict:
    base_url, key = _require_enabled()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(f"{base_url}/auth/v1{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read().decode()
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        try:
            body = json.loads(exc.read().decode())
        except Exception:
            body = {}
        message = str(body.get("msg") or body.get("message") or body.get("error_description") or "Authentication request failed.")
        raise SupabaseAuthError(message) from exc
    except (URLError, TimeoutError) as exc:
        raise SupabaseAuthError("The authentication service is temporarily unavailable.") from exc


def _user_from_response(response: dict) -> CurrentUser:
    metadata = response.get("user_metadata") or response.get("raw_user_meta_data") or {}
    email = str(response.get("email") or "unknown@example.com")
    return CurrentUser(
        id=str(response.get("id") or email),
        email=email,
        display_name=str(metadata.get("display_name") or metadata.get("name") or email),
        role=UserRole.VIEWER,
        department="operations",
    )


def start_viewer_signup(display_name: str, email: str, password: str) -> None:
    _request(
        "/signup",
        payload={
            "email": email.strip().lower(),
            "password": password,
            "data": {
                "display_name": display_name.strip(),
                "role": UserRole.VIEWER.value,
                "department": "operations",
            },
        },
    )


def confirm_viewer_signup(email: str, verification_code: str) -> None:
    _request(
        "/verify",
        payload={
            "email": email.strip().lower(),
            "token": verification_code,
            "type": "signup",
        },
    )


def login(email: str, password: str) -> tuple[str, int, CurrentUser]:
    query = urlencode({"grant_type": "password"})
    response = _request(
        f"/token?{query}",
        payload={"email": email.strip().lower(), "password": password},
    )
    token = str(response.get("access_token") or "")
    if not token:
        raise SupabaseAuthError("Email or password is incorrect, or the account is not verified.")
    expires_in = int(response.get("expires_in") or 3600)
    user = response.get("user") or {}
    return token, expires_in, _user_from_response(user)


def current_user(access_token: str) -> CurrentUser:
    response = _request("/user", method="GET", token=access_token)
    return _user_from_response(response)
