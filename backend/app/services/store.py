"""Thread-safe demo repository.

The local MVP deliberately keeps data in memory. The CDK project provisions the
DynamoDB tables that replace this adapter in a production deployment.
"""

from collections import Counter
from datetime import UTC, datetime
from threading import RLock
from uuid import uuid4

from app.models.schemas import (
    AgentTaskResponse,
    BotCreate,
    BotResponse,
    ChatHistoryItem,
    MessageRole,
    VehicleResponse,
)


def _now() -> datetime:
    return datetime.now(UTC)


class DemoStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._bots: dict[str, BotResponse] = {}
        self._conversations: dict[str, list[ChatHistoryItem]] = {}
        self._conversation_owners: dict[str, str] = {}
        self._tasks: dict[str, AgentTaskResponse] = {}
        self._task_owners: dict[str, str] = {}
        self._message_counts: Counter[str] = Counter()
        self._vehicles = self._seed_vehicles()
        self._seed_bots()

    def _seed_bots(self) -> None:
        seeds = [
            BotResponse(
                id="technician",
                name="Technician Assistant",
                department="maintenance",
                description="Diagnoses vehicle alerts using manuals and service history.",
                system_prompt=(
                    "You are a cautious automotive technician. Explain likely causes, request "
                    "missing vehicle details, and never present a remote diagnosis as certain."
                ),
                knowledge_source_ids=["ev-safety-guide", "service-playbook"],
                is_shared=True,
                created_at=_now(),
            ),
            BotResponse(
                id="fleet-manager",
                name="Fleet Manager",
                department="operations",
                description="Summarizes fleet health, maintenance demand, and operational risk.",
                system_prompt=(
                    "You are a fleet operations analyst. Prioritize safety, availability, cost, "
                    "and clear next actions in every answer."
                ),
                knowledge_source_ids=["fleet-maintenance-policy"],
                is_shared=True,
                created_at=_now(),
            ),
            BotResponse(
                id="sales-copilot",
                name="Sales Copilot",
                department="sales",
                description="Builds concise, data-aware proposals for enterprise fleet customers.",
                system_prompt=(
                    "You are an enterprise automotive sales copilot. Ask for customer constraints "
                    "and clearly distinguish known facts from assumptions."
                ),
                knowledge_source_ids=["fleet-offers"],
                is_shared=True,
                created_at=_now(),
            ),
        ]
        self._bots = {bot.id: bot for bot in seeds}

    @staticmethod
    def _seed_vehicles() -> list[VehicleResponse]:
        return [
            VehicleResponse(
                id="FM-2048",
                model="E-Transit Pro",
                driver="Nadia El Amrani",
                location="Casablanca",
                battery_percent=82,
                health_score=96,
                status="active",
                next_service_days=24,
            ),
            VehicleResponse(
                id="FM-1187",
                model="Model Y LR",
                driver="Youssef Idrissi",
                location="Rabat",
                battery_percent=64,
                health_score=91,
                status="active",
                next_service_days=12,
            ),
            VehicleResponse(
                id="FM-3091",
                model="eSprinter Cargo",
                driver="Salma Benali",
                location="Tangier",
                battery_percent=41,
                health_score=72,
                status="attention",
                next_service_days=3,
            ),
            VehicleResponse(
                id="FM-4410",
                model="Ioniq 5 Fleet",
                driver="Omar Alaoui",
                location="Marrakesh",
                battery_percent=18,
                health_score=68,
                status="maintenance",
                next_service_days=0,
            ),
            VehicleResponse(
                id="FM-5524",
                model="ID. Buzz Cargo",
                driver="Imane Tazi",
                location="Agadir",
                battery_percent=76,
                health_score=89,
                status="active",
                next_service_days=18,
            ),
        ]

    def list_bots(self, shared_only: bool = False) -> list[BotResponse]:
        with self._lock:
            bots = list(self._bots.values())
        if shared_only:
            bots = [bot for bot in bots if bot.is_shared]
        return sorted(bots, key=lambda bot: bot.name.lower())

    def get_bot(self, bot_id: str) -> BotResponse | None:
        with self._lock:
            return self._bots.get(bot_id)

    def create_bot(self, payload: BotCreate) -> BotResponse:
        slug = "-".join(payload.name.lower().split())
        bot_id = f"{slug[:32]}-{uuid4().hex[:6]}"
        bot = BotResponse(
            id=bot_id,
            knowledge_source_ids=[],
            created_at=_now(),
            **payload.model_dump(),
        )
        with self._lock:
            self._bots[bot_id] = bot
        return bot

    def attach_source(self, bot_id: str, source_id: str) -> None:
        with self._lock:
            bot = self._bots[bot_id]
            if source_id not in bot.knowledge_source_ids:
                self._bots[bot_id] = bot.model_copy(
                    update={"knowledge_source_ids": [*bot.knowledge_source_ids, source_id]}
                )

    def add_message(
        self,
        conversation_id: str,
        owner_id: str,
        role: MessageRole,
        content: str,
    ) -> ChatHistoryItem:
        message = ChatHistoryItem(id=uuid4().hex, role=role, content=content, created_at=_now())
        with self._lock:
            existing_owner = self._conversation_owners.setdefault(conversation_id, owner_id)
            if existing_owner != owner_id:
                raise PermissionError("Conversation access denied.")
            self._conversations.setdefault(conversation_id, []).append(message)
        return message

    def get_history(self, conversation_id: str, owner_id: str) -> list[ChatHistoryItem]:
        with self._lock:
            existing_owner = self._conversation_owners.get(conversation_id)
            if existing_owner is not None and existing_owner != owner_id:
                raise PermissionError("Conversation access denied.")
            return list(self._conversations.get(conversation_id, []))

    def record_assistant_message(self, bot_id: str) -> None:
        with self._lock:
            self._message_counts[bot_id] += 1

    def save_task(self, task: AgentTaskResponse, owner_id: str) -> AgentTaskResponse:
        with self._lock:
            self._tasks[task.task_id] = task
            self._task_owners[task.task_id] = owner_id
        return task

    def get_task(
        self,
        task_id: str,
        requester_id: str,
        allow_all: bool = False,
    ) -> AgentTaskResponse | None:
        with self._lock:
            owner_id = self._task_owners.get(task_id)
            if owner_id is not None and owner_id != requester_id and not allow_all:
                raise PermissionError("Task access denied.")
            return self._tasks.get(task_id)

    def vehicles(self) -> list[VehicleResponse]:
        return list(self._vehicles)

    def usage(self) -> dict[str, object]:
        with self._lock:
            return {
                "total_messages": sum(self._message_counts.values()),
                "total_agent_runs": len(self._tasks),
                "active_conversations": len(self._conversations),
                "published_bots": sum(1 for bot in self._bots.values() if bot.is_shared),
                "messages_by_bot": dict(self._message_counts),
            }


store = DemoStore()
