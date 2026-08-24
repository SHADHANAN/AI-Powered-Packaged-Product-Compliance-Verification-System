from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.verification_controller import VerificationController
from backend.schemas.verification import (
    VerificationListResponse,
    VerificationDetailResponse,
    VerificationReportResponse,
)

router = APIRouter(prefix="/verifications", tags=["Verifications"])


@router.get(
    "",
    response_model=VerificationListResponse,
    summary="List verification history",
    description="Retrieves a paginated list of previous packaged commodity compliance verifications.",
)
async def list_verifications(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
) -> VerificationListResponse:
    return VerificationController.list_verifications(db=db, skip=skip, limit=limit)


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


@router.get(
    "/{verification_id}/report",
    response_model=VerificationReportResponse,
    summary="Generate compliance audit report",
    description="Generates a downloadable compliance report with markdown text for a verification session.",
)
async def get_verification_report(
    verification_id: int,
    db: Session = Depends(get_db),
) -> VerificationReportResponse:
    report = VerificationController.generate_verification_report(
        db=db, verification_id=verification_id
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification with id {verification_id} not found",
        )
    return report
