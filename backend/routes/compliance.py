from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.compliance_controller import ComplianceController
from backend.schemas.compliance import (
    ComplianceEvaluationRequest,
    ComplianceEvaluationResponse,
)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post(
    "/evaluate",
    response_model=ComplianceEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Legal Metrology compliance",
    description=(
        "Evaluates packaged commodity declarations against mandatory Legal Metrology rules "
        "(including product identity, metric net quantity, MRP, manufacturer/importer presence, "
        "country of origin, dates, and consumer care details). Calculates a deterministic compliance "
        "score (0-100), overall status, and persists compliance checks to the verification database."
    ),
)
async def evaluate_compliance(
    request: ComplianceEvaluationRequest,
    db: Session = Depends(get_db),
) -> ComplianceEvaluationResponse:
    return ComplianceController.evaluate_compliance(db=db, request=request)
