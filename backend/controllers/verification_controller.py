from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from backend.database.models import Verification, ExtractedField, ComplianceCheck
from backend.schemas.verification import VerificationCreate


class VerificationController:
    """
    Controller handling database operations for Verification entity.
    """

    @staticmethod
    def get_verification_by_id(
        db: Session, verification_id: int
    ) -> Optional[Verification]:
        """
        Retrieves a verification record with eagerly loaded relationships:
        product, extracted_fields, and compliance_checks.
        """
        stmt = (
            select(Verification)
            .where(Verification.id == verification_id)
            .options(
                selectinload(Verification.product),
                selectinload(Verification.extracted_fields),
                selectinload(Verification.compliance_checks),
            )
        )
        return db.scalars(stmt).first()

    @staticmethod
    def create_verification(
        db: Session, verification_in: VerificationCreate
    ) -> Verification:
        """
        Creates a verification record in the database.
        """
        db_verification = Verification(**verification_in.model_dump())
        db.add(db_verification)
        db.commit()
        db.refresh(db_verification)
        return db_verification
