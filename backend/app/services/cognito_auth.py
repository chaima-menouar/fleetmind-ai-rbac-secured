"""Amazon Cognito adapter for real viewer email verification and sign-in."""

from functools import lru_cache

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.schemas import CurrentUser, UserRole


class CognitoAuthError(ValueError):
    """Safe error that can be returned to the API caller."""


@lru_cache
def _client():
    return boto3.client("cognito-idp", region_name=settings.aws_region)


def _require_enabled() -> str:
    client_id = settings.cognito_client_id.strip()
    if not client_id:
        raise CognitoAuthError("Email verification is not configured yet.")
    return client_id


def _attributes(response: dict) -> dict[str, str]:
    return {
        str(item.get("Name", "")): str(item.get("Value", ""))
        for item in response.get("UserAttributes", [])
    }


def _user_from_access_token(access_token: str) -> CurrentUser:
    try:
        response = _client().get_user(AccessToken=access_token)
    except ClientError as exc:
        raise CognitoAuthError("The session is invalid or expired.") from exc

    attributes = _attributes(response)
    role_value = attributes.get("custom:role", UserRole.VIEWER.value)
    try:
        role = UserRole(role_value)
    except ValueError:
        role = UserRole.VIEWER

    email = attributes.get("email", "unknown@example.com")
    return CurrentUser(
        id=str(response.get("Username", email)),
        email=email,
        display_name=attributes.get("name", email),
        role=role,
        department=attributes.get("custom:department", "operations"),
    )


def start_viewer_signup(display_name: str, email: str, password: str) -> None:
    client_id = _require_enabled()
    normalized_email = email.strip().lower()
    try:
        _client().sign_up(
            ClientId=client_id,
            Username=normalized_email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": normalized_email},
                {"Name": "name", "Value": display_name.strip()},
            ],
        )
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code == "UsernameExistsException":
            raise CognitoAuthError("An account already exists for this email.") from exc
        if code in {"InvalidPasswordException", "InvalidParameterException"}:
            raise CognitoAuthError("The registration details do not meet the account requirements.") from exc
        raise CognitoAuthError("The verification email could not be sent.") from exc


def confirm_viewer_signup(email: str, verification_code: str) -> None:
    client_id = _require_enabled()
    try:
        _client().confirm_sign_up(
            ClientId=client_id,
            Username=email.strip().lower(),
            ConfirmationCode=verification_code,
        )
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"CodeMismatchException", "ExpiredCodeException"}:
            raise CognitoAuthError("The verification code is incorrect or expired.") from exc
        raise CognitoAuthError("The account could not be verified.") from exc


def login(email: str, password: str) -> tuple[str, int, CurrentUser]:
    client_id = _require_enabled()
    try:
        response = _client().initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email.strip().lower(),
                "PASSWORD": password,
            },
        )
    except ClientError as exc:
        raise CognitoAuthError("Email or password is incorrect, or the account is not verified.") from exc

    result = response.get("AuthenticationResult") or {}
    token = str(result.get("AccessToken", ""))
    if not token:
        raise CognitoAuthError("Cognito did not return a valid access token.")
    expires_in = int(result.get("ExpiresIn", 3600))
    return token, expires_in, _user_from_access_token(token)


def current_user(access_token: str) -> CurrentUser:
    _require_enabled()
    return _user_from_access_token(access_token)
