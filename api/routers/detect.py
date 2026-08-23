"""Real-Time Fraud Detection API Router."""

import time
from fastapi import APIRouter
from api.schemas import (
    BatchDetectionRequest,
    BatchDetectionResponse,
    DetectionRequest,
    DetectionResponse,
)
from defend.ensemble import DetectionGrid

router = APIRouter(prefix="/api/detect", tags=["Detection Grid"])
detection_grid = DetectionGrid()


@router.post("", response_model=DetectionResponse)
def score_single_transaction(req: DetectionRequest):
    """Evaluate a single transaction through the sub-30ms cascading detection grid."""
    res = detection_grid.score_transaction(req.transaction, generate_sar=req.generate_sar)
    return DetectionResponse(**res)


@router.post("/batch", response_model=BatchDetectionResponse)
def score_transaction_batch(req: BatchDetectionRequest):
    """Batch score a collection of transactions and measure throughput."""
    t0 = time.perf_counter()
    results = []
    for txn in req.transactions:
        res = detection_grid.score_transaction(txn)
        results.append(DetectionResponse(**res))

    total_time = (time.perf_counter() - t0) * 1000.0
    mean_lat = total_time / max(1, len(req.transactions))

    return BatchDetectionResponse(
        total_scored=len(results),
        results=results,
        mean_latency_ms=round(mean_lat, 3),
    )
