"""Resource-level authorization rules shared by API routers."""

from fastapi import HTTPException, status

from app.models.schemas import BotResponse, CurrentUser, Department, UserRole

_TECHNICIAN_DEPARTMENTS = {
    Department.MAINTENANCE,
    Department.ENGINEERING,
    Department.SUPPORT,
}


def can_access_bot(user: CurrentUser, bot: BotResponse) -> bool:
    if user.role is UserRole.ADMIN:
        return True
    return user.role is UserRole.TECHNICIAN and bot.department in _TECHNICIAN_DEPARTMENTS


def ensure_bot_access(user: CurrentUser, bot: BotResponse) -> None:
    if not can_access_bot(user, bot):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This assistant is not available for your role.",
        )
