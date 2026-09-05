"""Authentication and role-based authorization for demo and Cognito modes."""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings
from app.models.schemas import CurrentUser, UserRole
from app.services.cognito_auth import CognitoAuthError, current_user as cognito_current_user

_DEMO_SIGNING_KEY = (settings.demo_auth_secret or secrets.token_urlsafe(48)).encode()


def _unauthorized(detail: str = "A valid session is required.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_demo_access_token(user: CurrentUser) -> tuple[str, int]:
    now = int(time.time())
    expires_in = settings.demo_token_ttl_seconds
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.display_name,
        "role": user.role.value,
        "department": user.department,
        "iat": now,
        "exp": now + expires_in,
        "iss": "fleetmind-demo",
    }
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(_DEMO_SIGNING_KEY, encoded_payload.encode(), hashlib.sha256).digest()
    return f"{encoded_payload}.{_b64encode(signature)}", expires_in


def _user_from_demo_token(token: str) -> CurrentUser:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        expected = hmac.new(_DEMO_SIGNING_KEY, encoded_payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(encoded_signature)):
            raise ValueError("signature")
        payload = json.loads(_b64decode(encoded_payload))
        if not isinstance(payload, dict):
            raise ValueError("payload")
        if payload.get("iss") != "fleetmind-demo" or int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired")
        role = UserRole(str(payload["role"]))
        return CurrentUser(
            id=str(payload["sub"]),
            email=str(payload["email"]),
            display_name=str(payload["name"]),
            role=role,
            department=str(payload["department"]),
        )
    except (
        AttributeError,
        binascii.Error,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        raise _unauthorized("The session is invalid or expired.") from exc


def _claims_from_api_gateway(request: Request) -> dict[str, Any]:
    event = request.scope.get("aws.event", {})
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )


def _cognito_role(claims: dict[str, Any]) -> UserRole:
    explicit_role = str(claims.get("custom:role", "")).strip().lower()
    if explicit_role in {role.value for role in UserRole}:
        return UserRole(explicit_role)

    raw_groups = claims.get("cognito:groups", [])
    if isinstance(raw_groups, str):
        cleaned = raw_groups.replace("[", "").replace("]", "")
        groups = {item.strip().strip("'\"").lower() for item in cleaned.split(",")}
    else:
        groups = {str(item).strip().lower() for item in raw_groups}
    if groups & {"admin", "manager"}:
        return UserRole.ADMIN
    if "technician" in groups:
        return UserRole.TECHNICIAN
    return UserRole.VIEWER


def get_current_user(request: Request) -> CurrentUser:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized()

    if settings.demo_mode and token.count(".") == 1:
        return _user_from_demo_token(token)

    if settings.cognito_enabled:
        try:
            return cognito_current_user(token)
        except CognitoAuthError as exc:
            raise _unauthorized(str(exc)) from exc

    claims = _claims_from_api_gateway(request)
    if claims:
        return CurrentUser(
            id=str(claims.get("sub", "unknown")),
            email=str(claims.get("email", "unknown@example.com")),
            display_name=str(claims.get("name", claims.get("email", "FleetMind user"))),
            role=_cognito_role(claims),
            department=str(claims.get("custom:department", "operations")),
        )

    raise _unauthorized("A verified session is required.")


def require_roles(*roles: UserRole) -> Callable[..., CurrentUser]:
    allowed = frozenset(roles)

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return user

    return dependency


require_admin = require_roles(UserRole.ADMIN)
require_operator = require_roles(UserRole.ADMIN, UserRole.TECHNICIAN)
require_chat_user = require_roles(UserRole.ADMIN, UserRole.TECHNICIAN, UserRole.VIEWER)
