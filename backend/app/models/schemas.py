"""Validated request and response contracts shared by the API."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Department(StrEnum):
    MAINTENANCE = "maintenance"
    OPERATIONS = "operations"
    SALES = "sales"
    SUPPORT = "support"
    ENGINEERING = "engineering"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class TaskStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class UserRole(StrEnum):
    ADMIN = "admin"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class ChatMessageRequest(BaseModel):
    conversation_id: str | None = None
    bot_id: str = "technician"
    content: str = Field(min_length=1, max_length=4_000)


class ChatMessageResponse(BaseModel):
    conversation_id: str
    bot_id: str
    content: str
    sources: list[str] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryItem(BaseModel):
    id: str
    role: MessageRole
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[ChatHistoryItem]


class BotCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80)
    department: Department
    description: str = Field(min_length=10, max_length=240)
    system_prompt: str = Field(min_length=20, max_length=4_000)
    is_shared: bool = False


class BotResponse(BotCreate):
    id: str
    knowledge_source_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class KnowledgeUploadResponse(BaseModel):
    bot_id: str
    source_id: str
    chunks_created: int


class AgentTaskRequest(BaseModel):
    task_type: str = "maintenance_triage"
    vehicle_id: str = Field(min_length=3, max_length=40)
    issue: str | None = Field(default=None, max_length=500)


class AgentTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    summary: str
    output: dict[str, Any]
    created_at: datetime


class VehicleResponse(BaseModel):
    id: str
    model: str
    driver: str
    location: str
    battery_percent: int = Field(ge=0, le=100)
    health_score: int = Field(ge=0, le=100)
    status: str
    next_service_days: int = Field(ge=0)


class FleetSummaryResponse(BaseModel):
    total_vehicles: int
    active_vehicles: int
    maintenance_due: int
    average_health: float
    vehicles: list[VehicleResponse]


class UsageStatsResponse(BaseModel):
    total_messages: int
    total_agent_runs: int
    active_conversations: int
    published_bots: int
    messages_by_bot: dict[str, int]


class ModelDatasetInfo(BaseModel):
    name: str
    source: str
    doi: str
    archive_sha256: str
    license_catalog: str
    train_rows: int
    test_rows: int
    features: int
    train_positive_rows: int
    test_positive_rows: int


class ModelTrainingInfo(BaseModel):
    random_state: int
    fit_rows: int
    calibration_rows: int
    threshold_rows: int
    decision_threshold: float = Field(ge=0, le=1)
    validation_cost: int
    false_positive_cost: int
    false_negative_cost: int


class ModelMetrics(BaseModel):
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1: float = Field(ge=0, le=1)
    balanced_accuracy: float = Field(ge=0, le=1)
    roc_auc: float = Field(ge=0, le=1)
    average_precision: float = Field(ge=0, le=1)
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int
    official_cost: int
    all_negative_baseline_cost: int
    cost_reduction_percent: float = Field(ge=0, le=100)


class ModelRuntimeInfo(BaseModel):
    python: str
    scikit_learn: str
    numpy: str
    pandas: str


class ModelCardResponse(BaseModel):
    model_version: str
    artifact_sha256: str
    trained_at: datetime
    algorithm: str
    dataset: ModelDatasetInfo
    training: ModelTrainingInfo
    metrics: ModelMetrics
    runtime: ModelRuntimeInfo
    limitations: list[str]


class PredictionSampleResponse(BaseModel):
    sample_id: str


class PredictionRequest(BaseModel):
    sample_id: str = Field(min_length=3, max_length=80)


class PredictionResponse(BaseModel):
    sample_id: str
    aps_failure_score: float = Field(ge=0, le=1)
    decision_threshold: float = Field(ge=0, le=1)
    predicted_label: str
    actual_label: str
    matches_actual: bool
    risk_level: str
    model_version: str


class CurrentUser(BaseModel):
    id: str
    email: str
    display_name: str
    role: UserRole
    department: str


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class ViewerRegistrationRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=256)
    verification_code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class AuthSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: CurrentUser


class ApiMessage(BaseModel):
    message: str
