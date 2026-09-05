"""Optional DynamoDB persistence used by the AWS deployment path.

The application keeps a credential-free in-memory store for local demos. When the
CDK table names are present, this adapter persists user-created assistants,
conversation messages, and agent tasks without changing the API contracts.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.models.schemas import AgentTaskResponse, BotResponse, ChatHistoryItem


@lru_cache(maxsize=1)
def _dynamodb_resource() -> Any:
    import boto3

    return boto3.resource("dynamodb", region_name=settings.aws_region)


class DynamoCloudStore:
    @property
    def conversations_enabled(self) -> bool:
        return bool(settings.conversations_table)

    @property
    def bots_enabled(self) -> bool:
        return bool(settings.bots_table)

    @property
    def tasks_enabled(self) -> bool:
        return bool(settings.tasks_table)

    @property
    def enabled(self) -> bool:
        return self.conversations_enabled or self.bots_enabled or self.tasks_enabled

    def _table(self, table_name: str) -> Any:
        return _dynamodb_resource().Table(table_name)

    def put_bot(self, bot: BotResponse) -> None:
        if not self.bots_enabled or not settings.bots_table:
            return
        self._table(settings.bots_table).put_item(Item=bot.model_dump(mode="json"))

    def get_bot(self, bot_id: str) -> BotResponse | None:
        if not self.bots_enabled or not settings.bots_table:
            return None
        item = self._table(settings.bots_table).get_item(Key={"id": bot_id}).get("Item")
        return BotResponse.model_validate(item) if item else None

    def list_bots(self) -> list[BotResponse]:
        if not self.bots_enabled or not settings.bots_table:
            return []
        response = self._table(settings.bots_table).scan()
        items = list(response.get("Items", []))
        while response.get("LastEvaluatedKey"):
            response = self._table(settings.bots_table).scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))
        return [BotResponse.model_validate(item) for item in items]

    def put_message(
        self,
        conversation_id: str,
        owner_id: str,
        message: ChatHistoryItem,
    ) -> None:
        if not self.conversations_enabled or not settings.conversations_table:
            return
        payload = message.model_dump(mode="json")
        self._table(settings.conversations_table).put_item(
            Item={
                "conversationId": conversation_id,
                "createdAt": payload["created_at"],
                "ownerId": owner_id,
                "message": payload,
            }
        )

    def get_history(self, conversation_id: str, owner_id: str) -> list[ChatHistoryItem] | None:
        if not self.conversations_enabled or not settings.conversations_table:
            return None
        from boto3.dynamodb.conditions import Key

        response = self._table(settings.conversations_table).query(
            KeyConditionExpression=Key("conversationId").eq(conversation_id),
            ScanIndexForward=True,
        )
        items = list(response.get("Items", []))
        if not items:
            return []
        if any(str(item.get("ownerId", "")) != owner_id for item in items):
            raise PermissionError("Conversation access denied.")
        return [ChatHistoryItem.model_validate(item["message"]) for item in items]

    def put_task(self, task: AgentTaskResponse, owner_id: str) -> None:
        if not self.tasks_enabled or not settings.tasks_table:
            return
        self._table(settings.tasks_table).put_item(
            Item={
                "taskId": task.task_id,
                "ownerId": owner_id,
                "task": task.model_dump(mode="json"),
            }
        )

    def get_task(
        self,
        task_id: str,
        requester_id: str,
        allow_all: bool = False,
    ) -> AgentTaskResponse | None:
        if not self.tasks_enabled or not settings.tasks_table:
            return None
        item = self._table(settings.tasks_table).get_item(Key={"taskId": task_id}).get("Item")
        if not item:
            return None
        owner_id = str(item.get("ownerId", ""))
        if owner_id != requester_id and not allow_all:
            raise PermissionError("Task access denied.")
        return AgentTaskResponse.model_validate(item["task"])


cloud_store = DynamoCloudStore()
