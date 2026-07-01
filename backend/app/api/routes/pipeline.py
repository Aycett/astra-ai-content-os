"""Pipeline endpoints."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.pipeline import run_mock_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineRunRequest(BaseModel):
    """Request body for running the mock content pipeline."""

    topic: str = Field(min_length=1, description="Topic to research and produce content for.")


@router.post("/run")
def run_pipeline(request: PipelineRunRequest) -> dict[str, Any]:
    """Run the full mock content pipeline for a topic."""
    return run_mock_pipeline(request.topic)
