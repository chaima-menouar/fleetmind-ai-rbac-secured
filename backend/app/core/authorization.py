"""Resource-level authorization rules shared by API routers."""

from fastapi import HTTPException, status

from app.models.schemas import BotResponse, CurrentUser, UserRole

_ROLE_BOTS = {
    UserRole.ADMIN: {"fleet-manager"},
    UserRole.TECHNICIAN: {"technician"},
    UserRole.VIEWER: {"viewer-assistant"},
}


def can_access_bot(user: CurrentUser, bot: BotResponse) -> bool:
    return bot.id in _ROLE_BOTS.get(user.role, set())


def ensure_bot_access(user: CurrentUser, bot: BotResponse) -> None:
    if not can_access_bot(user, bot):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This assistant is not available for your role.",
        )
