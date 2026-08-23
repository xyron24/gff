"""Closed-Loop Co-Evolution API Router."""

from typing import Any, Dict, List
from fastapi import APIRouter
from api.schemas import RunEpochRequest, RunEpochResponse
from closed_loop.loop_orchestrator import ClosedLoopOrchestrator

router = APIRouter(prefix="/api/loop", tags=["Closed-Loop Co-Evolution"])
orchestrator = ClosedLoopOrchestrator()


@router.post("/run-epoch", response_model=RunEpochResponse)
def run_co_evolution_epoch(req: RunEpochRequest):
    """Trigger one complete closed-loop co-evolution epoch."""
    epoch_record = orchestrator.run_epoch(
        n_transactions=req.n_transactions,
        fraud_ratio=req.fraud_ratio,
        retrain_defense=req.retrain_defense,
    )
    return RunEpochResponse(epoch_record=epoch_record)


@router.get("/history", response_model=List[Dict[str, Any]])
def get_co_evolution_history():
    """Retrieve full chronological trajectory of co-evolution epochs and recall lift curves."""
    return orchestrator.epoch_history
