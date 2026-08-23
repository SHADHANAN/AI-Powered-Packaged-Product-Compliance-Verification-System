from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.database.models import Verification, ComplianceCheck, ExtractedField, Product
from services.explanation_service import (
    build_evidence_context,
    ExplanationReportGenerator,
    ExplanationResult,
)
from backend.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ExplanationItem,
)
from backend.utils.logger import logger


class ExplanationController:
    """
    Controller coordinating legal explanation and remediation advice generation.
    """

    @staticmethod
    def generate_explanation(
        db: Session,
        request: ExplanationRequest,
    ) -> ExplanationResponse:
        """
        Gathers verified compliance evidence and generates human-readable explanations.
        """
        verification: Optional[Verification] = None

        if request.verification_id is not None:
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

            checks_source = verification.compliance_checks or []
            overall_score = float(verification.overall_score or 0.0)
            overall_status = (verification.verification_status or "PENDING").upper()
            product_name = verification.product.product_name if verification.product else None

            context = build_evidence_context(
                checks=checks_source,
                overall_score=overall_score,
                overall_status=overall_status,
                extracted_fields=verification.extracted_fields,
                product_name=product_name,
            )
        else:
            # Standalone evaluation from request payload
            checks_source = request.checks or []
            overall_score = float(request.overall_score if request.overall_score is not None else 100.0)
            overall_status = (request.status or "COMPLIANT").upper()

            context = build_evidence_context(
                checks=checks_source,
                overall_score=overall_score,
                overall_status=overall_status,
            )

        # Generate report
        report: ExplanationResult = ExplanationReportGenerator.generate_report(context)

        explanation_items = [
            ExplanationItem(
                rule_code=item.rule_code,
                rule_name=item.rule_name,
                severity=item.severity,
                status=item.status,
                explanation=item.explanation,
                why_it_matters=item.why_it_matters,
                recommended_action=item.recommended_action,
                evidence=item.evidence,
                confidence=item.confidence,
            )
            for item in report.explanations
        ]

        return ExplanationResponse(
            success=True,
            verification_id=verification.id if verification else None,
            overall_status=report.overall_status,
            overall_score=report.overall_score,
            summary=report.summary,
            explanations=explanation_items,
            recommendations=report.recommendations,
            ai_generated=report.ai_generated,
            error_message=report.error_message,
        )
