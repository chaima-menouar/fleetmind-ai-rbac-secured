"""Session endpoints for the local demo and Cognito-authenticated users."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_demo_access_token, get_current_user
from app.models.schemas import (
    AuthSessionResponse,
    CurrentUser,
    LoginRequest,
    ViewerRegistrationRequest,
)
from app.services.demo_auth import demo_auth

router = APIRouter()


def _session(user: CurrentUser) -> AuthSessionResponse:
    token, expires_in = create_demo_access_token(user)
    return AuthSessionResponse(access_token=token, expires_in=expires_in, user=user)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest) -> AuthSessionResponse:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use the configured Cognito sign-in flow.",
        )
    user = demo_auth.authenticate(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
        )
    return _session(user)


@router.post(
    "/register-viewer",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_viewer(payload: ViewerRegistrationRequest) -> AuthSessionResponse:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viewer provisioning is managed by Cognito in production.",
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
    return _session(user)


@router.get("/me", response_model=CurrentUser)
def current_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
