"""Mastercard AI Defense Lab - High-Performance FastAPI Engine.

Main application entry point exposing REST endpoints and WebSocket stream.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from api.routers import attacks, dashboard, detect, generate, loop
from api.schemas import SystemHealthResponse
from api.ws import handle_transaction_websocket
from identify.loader import get_default_registry

load_dotenv()

app = FastAPI(
    title="Mastercard AI Defense Lab API",
    description="Autonomous Closed-Loop Red-Team / Blue-Team AI Defense Lab for Payment Security",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Next.js Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(attacks.router)
app.include_router(generate.router)
app.include_router(detect.router)
app.include_router(dashboard.router)
app.include_router(loop.router)


@app.get("/health", response_model=SystemHealthResponse, tags=["Health"])
def system_health():
    """System health check and component status."""
    registry = get_default_registry()
    return SystemHealthResponse(
        status="HEALTHY",
        version="1.0.0",
        models_ready=True,
        total_attacks_registered=registry.count(),
        replay_buffer_size=loop.orchestrator.replay_buffer.size(),
        co_evolution_epochs_completed=len(loop.orchestrator.epoch_history),
    )


@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    """High-frequency real-time transaction streaming endpoint."""
    await handle_transaction_websocket(websocket)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
