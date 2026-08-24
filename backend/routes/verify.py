from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.verification_pipeline_controller import VerificationPipelineController
from backend.schemas.pipeline import VerificationPipelineResponse

router = APIRouter(prefix="/verify", tags=["End-to-End Verification Pipeline"])


@router.post(
    "",
    response_model=VerificationPipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute complete end-to-end packaged product compliance verification",
    description=(
        "Performs complete verification pipeline on an uploaded product image: "
        "1. Image validation & preprocessing -> "
        "2. PaddleOCR text recognition -> "
        "3. NLP field extraction & normalization -> "
        "4. Product & Verification DB record creation -> "
        "5. ExtractedField persistence -> "
        "6. Deterministic Legal Metrology RuleEngine evaluation -> "
        "7. ComplianceCheck DB persistence & scoring -> "
        "8. Evidence-grounded AI legal explanation & remediation advice -> "
        "9. Structured consolidated verification response."
    ),
)
async def verify_packaged_product(
    image: UploadFile = File(..., description="Uploaded packaged product image (JPEG, PNG, WEBP)"),
    preprocessing_strategy: Optional[str] = Form(
        "standard",
        description="Preprocessing pipeline: 'standard', 'grayscale_clahe', 'binarized', or 'raw'",
    ),
    db: Session = Depends(get_db),
) -> VerificationPipelineResponse:
    return await VerificationPipelineController.verify_image(
        db=db,
        image=image,
        preprocessing_strategy=preprocessing_strategy,
    )
