"""Internal bot configuration used by services and import scripts."""

from pydantic import BaseModel, Field


class BotConfig(BaseModel):
    id: str
    name: str
    department: str  # e.g. "maintenance", "sales", "support"
    system_prompt: str
    knowledge_source_ids: list[str] = Field(default_factory=list)
    is_shared: bool = False  # visible in internal marketplace
