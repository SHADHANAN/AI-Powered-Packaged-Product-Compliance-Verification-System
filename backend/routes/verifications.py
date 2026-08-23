from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.verification_controller import VerificationController
from backend.schemas.verification import VerificationDetailResponse

router = APIRouter(prefix="/verifications", tags=["Verifications"])


@router.get(
    "/{verification_id}",
    response_model=VerificationDetailResponse,
    summary="Get verification details by ID",
    description=(
        "Retrieves detailed compliance verification information including the "
        "associated product, extracted package fields, and compliance check results."
    ),
)
async def get_verification(
    verification_id: int,
    db: Session = Depends(get_db),
) -> VerificationDetailResponse:
    verification = VerificationController.get_verification_by_id(
        db=db, verification_id=verification_id
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification with id {verification_id} not found",
        )
    return verification
