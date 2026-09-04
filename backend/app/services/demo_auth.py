"""Server-side credentials for the credential-free local demonstration.

This adapter exists only when ``DEMO_MODE=true``. Production authentication is
owned by Amazon Cognito and API Gateway; the browser never gets to choose a
role in either mode.
"""

from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes
from threading import RLock
from uuid import uuid4

from app.core.config import settings
from app.models.schemas import CurrentUser, UserRole


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
        raise ValueError("Enter a valid email address.")
    return normalized


def _validate_password(password: str) -> None:
    checks = (
        any(character.islower() for character in password),
        any(character.isupper() for character in password),
        any(character.isdigit() for character in password),
        any(not character.isalnum() for character in password),
    )
    if len(password) < 12 or not all(checks):
        raise ValueError(
            "Password must be at least 12 characters and include upper-case, lower-case, "
            "number, and symbol characters."
        )


@dataclass(frozen=True)
class _ViewerCredential:
    user: CurrentUser
    salt: bytes
    password_hash: bytes


class DemoAuthService:
    def __init__(self) -> None:
        self._lock = RLock()
        self._viewers: dict[str, _ViewerCredential] = {}
        self._company_accounts = {
            "manager@fleetmind.demo": (
                settings.demo_manager_password,
                CurrentUser(
                    id="manager-01",
                    email="manager@fleetmind.demo",
                    display_name="Fleet Manager",
                    role=UserRole.ADMIN,
                    department="operations",
                ),
            ),
            "technician@fleetmind.demo": (
                settings.demo_technician_password,
                CurrentUser(
                    id="technician-01",
                    email="technician@fleetmind.demo",
                    display_name="Service Technician",
                    role=UserRole.TECHNICIAN,
                    department="maintenance",
                ),
            ),
            "viewer@fleetmind.demo": (
                settings.demo_viewer_password,
                CurrentUser(
                    id="viewer-01",
                    email="viewer@fleetmind.demo",
                    display_name="Fleet Viewer",
                    role=UserRole.VIEWER,
                    department="operations",
                ),
            ),
        }

    def authenticate(self, email: str, password: str) -> CurrentUser | None:
        try:
            normalized = _normalize_email(email)
        except ValueError:
            return None
        company_account = self._company_accounts.get(normalized)
        if company_account and compare_digest(company_account[0], password):
            return company_account[1]

        with self._lock:
            viewer = self._viewers.get(normalized)
        if viewer is None:
            return None
        candidate = pbkdf2_hmac("sha256", password.encode(), viewer.salt, 310_000)
        return viewer.user if compare_digest(candidate, viewer.password_hash) else None

    def register_viewer(
        self,
        display_name: str,
        email: str,
        password: str,
        verification_code: str,
    ) -> CurrentUser:
        normalized = _normalize_email(email)
        clean_name = display_name.strip()
        if len(clean_name) < 2:
            raise ValueError("Enter your full name.")
        _validate_password(password)
        if not compare_digest(verification_code, settings.demo_verification_code):
            raise ValueError("The verification code is incorrect.")

        with self._lock:
            if normalized in self._company_accounts or normalized in self._viewers:
                raise ValueError("An account already exists for this email.")
            salt = token_bytes(16)
            user = CurrentUser(
                id=f"viewer-{uuid4().hex}",
                email=normalized,
                display_name=clean_name,
                role=UserRole.VIEWER,
                department="operations",
            )
            self._viewers[normalized] = _ViewerCredential(
                user=user,
                salt=salt,
                password_hash=pbkdf2_hmac("sha256", password.encode(), salt, 310_000),
            )
        return user


demo_auth = DemoAuthService()
