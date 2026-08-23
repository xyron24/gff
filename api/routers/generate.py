"""Synthetic Transaction & Attack Generation API Router."""

from fastapi import APIRouter
from api.schemas import GenerationRequest, GenerationResponse
from generate.pipeline import SimulationPipeline
from generate.iso20022_formatter import format_pacs008, format_pain001

router = APIRouter(prefix="/api/generate", tags=["Synthetic Simulation"])
pipeline = SimulationPipeline(random_seed=42)


@router.post("", response_model=GenerationResponse)
def generate_transactions(req: GenerationRequest):
    """Generate a batch of legitimate and synthetic fraud transactions."""
    df, summary = pipeline.generate_dataset(
        n_total=req.n_transactions,
        fraud_ratio=req.fraud_ratio,
        selected_attacks=req.selected_attacks,
    )

    records = []
    for _, row in df.iterrows():
        d = row.to_dict()
        if hasattr(d.get("timestamp"), "isoformat"):
            d["timestamp"] = d["timestamp"].isoformat()
        # Attach ISO 20022 XML snippet
        if d.get("channel") == "WIRE":
            d["iso_xml_preview"] = format_pain001(d)[:350] + "..."
        else:
            d["iso_xml_preview"] = format_pacs008(d)[:350] + "..."
        records.append(d)

    return GenerationResponse(
        summary=summary,
        transactions=records,
    )
