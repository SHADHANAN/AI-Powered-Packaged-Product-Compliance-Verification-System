from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.explanation_controller import ExplanationController
from backend.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
)

router = APIRouter(prefix="/explanation", tags=["Explanation & Recommendations"])


@router.post(
    "",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate evidence-grounded legal explanations and remediation advice",
    description=(
        "Consumes authoritative deterministic compliance results (from Phase 5) and generates "
        "human-readable legal explanations, statutory importance rationale, actionable remediation "
        "recommendations, and executive summaries. Supports seamless deterministic fallback when "
        "AI/LLM service is offline or unconfigured."
    ),
)
async def generate_explanation(
    request: ExplanationRequest,
    db: Session = Depends(get_db),
) -> ExplanationResponse:
    return ExplanationController.generate_explanation(db=db, request=request)
