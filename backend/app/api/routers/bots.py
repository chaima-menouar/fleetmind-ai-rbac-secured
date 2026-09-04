"""Custom bot and local knowledge endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.core.authorization import can_access_bot, ensure_bot_access
from app.core.config import settings
from app.core.security import require_admin, require_operator
from app.models.schemas import BotCreate, BotResponse, CurrentUser, KnowledgeUploadResponse
from app.rag.ingestion import ingest_document
from app.services.store import store

router = APIRouter()


@router.post("", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
def create_bot(
    payload: BotCreate,
    _: CurrentUser = Depends(require_admin),
) -> BotResponse:
    return store.create_bot(payload)


@router.get("", response_model=list[BotResponse])
def list_bots(
    shared_only: bool = Query(default=False),
    user: CurrentUser = Depends(require_operator),
) -> list[BotResponse]:
    return [
        bot
        for bot in store.list_bots(shared_only=shared_only)
        if can_access_bot(user, bot)
    ]


@router.get("/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: str, user: CurrentUser = Depends(require_operator)) -> BotResponse:
    bot = store.get_bot(bot_id)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found.")
    ensure_bot_access(user, bot)
    return bot


@router.post("/{bot_id}/knowledge", response_model=KnowledgeUploadResponse)
async def upload_knowledge(
    bot_id: str,
    file: UploadFile = File(...),
    _: CurrentUser = Depends(require_admin),
) -> KnowledgeUploadResponse:
    if store.get_bot(bot_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found.")
    content = await file.read(settings.max_upload_bytes + 1)
    try:
        source_id, chunks = ingest_document(
            bot_id,
            file.filename or "knowledge.txt",
            content,
            settings.max_upload_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    store.attach_source(bot_id, source_id)
    return KnowledgeUploadResponse(bot_id=bot_id, source_id=source_id, chunks_created=chunks)
