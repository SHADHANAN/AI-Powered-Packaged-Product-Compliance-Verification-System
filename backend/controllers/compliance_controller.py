from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload

from backend.database.models import Verification, ComplianceCheck, ExtractedField, Product
from services.compliance_service import RuleEngine, ComplianceEvaluationSummary
from backend.schemas.compliance import (
    ComplianceEvaluationRequest,
    ComplianceEvaluationResponse,
    ComplianceCheckResponse,
)
from backend.utils.logger import logger


class ComplianceController:
    """
    Controller handling Legal Metrology rule evaluation and persistence.
    """

    @staticmethod
    def evaluate_compliance(
        db: Session,
        request: ComplianceEvaluationRequest,
    ) -> ComplianceEvaluationResponse:
        """
        Runs the rule engine against packaging declarations and persists results when verification_id is present.
        """
        verification: Optional[Verification] = None
        fields_for_evaluation: Dict[str, Any] = {}

        if request.verification_id is not None:
            # Load verification with related product and extracted fields
            stmt = (
                select(Verification)
                .where(Verification.id == request.verification_id)
                .options(
                    selectinload(Verification.product),
                    selectinload(Verification.extracted_fields),
                    selectinload(Verification.compliance_checks),
                )
            )
            verification = db.scalars(stmt).first()
            if not verification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Verification with id {request.verification_id} not found",
                )

            # Assemble extracted fields from DB or request override
            if request.extracted_fields:
                for item in request.extracted_fields:
                    if isinstance(item, dict) and "field_name" in item:
                        fields_for_evaluation[item["field_name"]] = item
            elif verification.extracted_fields:
                for ef in verification.extracted_fields:
                    fields_for_evaluation[ef.field_name] = {
                        "field_name": ef.field_name,
                        "value": ef.field_value,
                        "confidence": ef.confidence,
                        "source_text": ef.source_text,
                    }
            elif verification.product:
                # Fallback to Product record attributes if no OCR extracted_fields exist yet
                prod = verification.product
                fields_for_evaluation = {
                    "product_name": prod.product_name,
                    "brand_name": prod.brand_name,
                    "manufacturer_name": prod.manufacturer_name,
                    "importer_name": prod.importer_name,
                    "country_of_origin": prod.country_of_origin,
                    "net_quantity": prod.net_quantity,
                    "unit": prod.unit,
                    "batch_number": prod.batch_number,
                    "date_of_manufacture": prod.date_of_manufacture,
                    "date_of_import": prod.date_of_import,
                    "mrp": prod.mrp,
                    "customer_care_details": prod.customer_care_details,
                }
        else:
            # Standalone evaluation without database persistence
            if request.extracted_fields:
                for item in request.extracted_fields:
                    if isinstance(item, dict) and "field_name" in item:
                        fields_for_evaluation[item["field_name"]] = item

        # Run Rule Engine
        summary: ComplianceEvaluationSummary = RuleEngine.evaluate_fields(fields_for_evaluation)

        check_responses: List[ComplianceCheckResponse] = []

        # If connected to a Verification in the DB, persist ComplianceCheck records
        if verification is not None:
            try:
                # Clear previous checks for this verification
                db.execute(
                    delete(ComplianceCheck).where(ComplianceCheck.verification_id == verification.id)
                )

                # Insert newly evaluated checks
                for chk in summary.checks:
                    db_check = ComplianceCheck(
                        verification_id=verification.id,
                        rule_code=chk.rule_code,
                        rule_name=chk.rule_name,
                        status=chk.status.lower(),
                        severity=chk.severity.lower(),
                        expected_value=chk.expected_value,
                        actual_value=chk.actual_value,
                        explanation=chk.explanation,
                    )
                    db.add(db_check)
                    check_responses.append(
                        ComplianceCheckResponse(
                            verification_id=verification.id,
                            rule_code=chk.rule_code,
                            rule_name=chk.rule_name,
                            status=chk.status,
                            severity=chk.severity,
                            expected_value=chk.expected_value,
                            actual_value=chk.actual_value,
                            explanation=chk.explanation,
                            created_at=datetime.now(timezone.utc),
                        )
                    )

                # Update verification record
                verification.verification_status = summary.status.lower()
                verification.overall_score = summary.overall_score
                verification.completed_at = datetime.now(timezone.utc)

                db.commit()
                db.refresh(verification)

            except Exception as e:
                db.rollback()
                logger.exception(f"Failed to persist compliance checks: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error during compliance check persistence: {str(e)}",
                )
        else:
            for chk in summary.checks:
                check_responses.append(
                    ComplianceCheckResponse(
                        rule_code=chk.rule_code,
                        rule_name=chk.rule_name,
                        status=chk.status,
                        severity=chk.severity,
                        expected_value=chk.expected_value,
                        actual_value=chk.actual_value,
                        explanation=chk.explanation,
                    )
                )

        return ComplianceEvaluationResponse(
            success=True,
            verification_id=verification.id if verification else None,
            status=summary.status,
            overall_score=summary.overall_score,
            checks=check_responses,
            total_rules_evaluated=summary.total_rules_evaluated,
            passed_count=summary.passed_count,
            failed_count=summary.failed_count,
            warning_count=summary.warning_count,
        )
