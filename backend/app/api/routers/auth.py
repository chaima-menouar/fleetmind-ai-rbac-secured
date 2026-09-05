"""Session endpoints for company demo accounts and Cognito viewer accounts."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_demo_access_token, get_current_user
from app.models.schemas import (
    ApiMessage,
    AuthSessionResponse,
    CurrentUser,
    LoginRequest,
    ViewerRegistrationRequest,
    ViewerSignupConfirmRequest,
    ViewerSignupStartRequest,
)
from app.services import cognito_auth
from app.services.cognito_auth import CognitoAuthError
from app.services.demo_auth import demo_auth

router = APIRouter()


def _demo_session(user: CurrentUser) -> AuthSessionResponse:
    token, expires_in = create_demo_access_token(user)
    return AuthSessionResponse(access_token=token, expires_in=expires_in, user=user)


def _cognito_session(email: str, password: str) -> AuthSessionResponse:
    try:
        token, expires_in, user = cognito_auth.login(email, password)
    except CognitoAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return AuthSessionResponse(access_token=token, expires_in=expires_in, user=user)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest) -> AuthSessionResponse:
    if settings.demo_mode:
        user = demo_auth.authenticate(payload.email, payload.password)
        if user is not None:
            return _demo_session(user)

    if settings.cognito_enabled:
        return _cognito_session(payload.email, payload.password)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email or password is incorrect.",
    )


@router.post(
    "/register-viewer/start",
    response_model=ApiMessage,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_viewer_registration(payload: ViewerSignupStartRequest) -> ApiMessage:
    if not settings.cognito_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verification is not configured yet.",
        )
    try:
        cognito_auth.start_viewer_signup(payload.display_name, payload.email, payload.password)
    except CognitoAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiMessage(message="Verification code sent to your email.")


@router.post("/register-viewer/confirm", response_model=ApiMessage)
def confirm_viewer_registration(payload: ViewerSignupConfirmRequest) -> ApiMessage:
    if not settings.cognito_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verification is not configured yet.",
        )
    try:
        cognito_auth.confirm_viewer_signup(payload.email, payload.verification_code)
    except CognitoAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiMessage(message="Email verified. You can now sign in.")


@router.post(
    "/register-viewer",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
)
def register_viewer_legacy(payload: ViewerRegistrationRequest) -> AuthSessionResponse:
    """Legacy local-only endpoint kept for automated/local demo compatibility."""
    if not settings.demo_mode or settings.cognito_enabled:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Use the email verification registration flow.",
        )
    try:
        user = demo_auth.register_viewer(
            payload.display_name,
            payload.email,
            payload.password,
            payload.verification_code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _demo_session(user)


@router.get("/me", response_model=CurrentUser)
def current_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
