"""Chat endpoints backed by RAG and the configured LLM gateway."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.authorization import ensure_bot_access
from app.core.security import require_chat_user
from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    CurrentUser,
    MessageRole,
)
from app.rag.retrieval import retrieve
from app.services.audit import emit
from app.services.llm_gateway import complete
from app.services.store import store

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    payload: ChatMessageRequest,
    user: CurrentUser = Depends(require_chat_user),
) -> ChatMessageResponse:
    bot = store.get_bot(payload.bot_id)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found.")
    ensure_bot_access(user, bot)

    conversation_id = payload.conversation_id or uuid4().hex
    try:
        store.add_message(conversation_id, user.id, MessageRole.USER, payload.content)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    context = retrieve(bot.id, payload.content)
    try:
        answer = complete(
            payload.content,
            system_prompt=bot.system_prompt,
            context=context,
            fleet=store.vehicles(),
        )
    except Exception as exc:
        emit(
            "assistant_request_failed",
            user_id=user.id,
            role=user.role.value,
            bot_id=bot.id,
            conversation_id=conversation_id,
            source_count=len(context),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The configured LLM provider could not complete the request.",
        ) from exc

    assistant_message = store.add_message(
        conversation_id,
        user.id,
        MessageRole.ASSISTANT,
        answer,
    )
    store.record_assistant_message(bot.id)
    sources = [item.split("]", 1)[0].lstrip("[") for item in context]
    emit(
        "assistant_request_completed",
        user_id=user.id,
        role=user.role.value,
        bot_id=bot.id,
        conversation_id=conversation_id,
        source_count=len(sources),
    )
    return ChatMessageResponse(
        conversation_id=conversation_id,
        bot_id=bot.id,
        content=assistant_message.content,
        sources=sources,
        created_at=assistant_message.created_at,
    )


@router.get("/history/{conversation_id}", response_model=ChatHistoryResponse)
def get_history(
    conversation_id: str,
    user: CurrentUser = Depends(require_chat_user),
) -> ChatHistoryResponse:
    try:
        messages = store.get_history(conversation_id, user.id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return ChatHistoryResponse(conversation_id=conversation_id, messages=messages)
