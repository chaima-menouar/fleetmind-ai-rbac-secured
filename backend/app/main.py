"""FleetMind AI FastAPI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import admin, agents, auth, bots, chat, fleet, ml
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI copilots and maintenance agents for enterprise vehicle fleets.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(bots.router, prefix="/api/bots", tags=["bots"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(fleet.router, prefix="/api/fleet", tags=["fleet"])
app.include_router(ml.router, prefix="/api/ml", tags=["predictive maintenance"])


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "demo_mode": settings.demo_mode,
    }
