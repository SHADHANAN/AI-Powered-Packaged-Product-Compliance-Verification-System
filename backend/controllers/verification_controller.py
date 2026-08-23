from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, selectinload
from backend.database.models import Verification, Product, ExtractedField, ComplianceCheck
from backend.schemas.verification import (
    VerificationCreate,
    VerificationListResponse,
    VerificationListItem,
    VerificationReportResponse,
)


class VerificationController:
    """
    Controller handling database operations and report generation for Verification entity.
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
    def list_verifications(
        db: Session, skip: int = 0, limit: int = 50
    ) -> VerificationListResponse:
        """
        Retrieves a paginated list of verification records with associated products, ordered by newest first.
        """
        total_stmt = select(func.count()).select_from(Verification)
        total = db.scalar(total_stmt) or 0

        stmt = (
            select(Verification)
            .options(selectinload(Verification.product))
            .order_by(desc(Verification.id))
            .offset(skip)
            .limit(limit)
        )
        verifications = list(db.scalars(stmt).all())

        items = [VerificationListItem.model_validate(v) for v in verifications]

        return VerificationListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

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

    @classmethod
    def generate_verification_report(
        cls, db: Session, verification_id: int
    ) -> Optional[VerificationReportResponse]:
        """
        Generates a comprehensive compliance audit report with markdown summary for a verification session.
        """
        v = cls.get_verification_by_id(db, verification_id)
        if not v:
            return None

        prod_name = v.product.product_name if v.product else "Unknown Product"
        brand_name = v.product.brand_name if v.product else None

        checks = v.compliance_checks or []
        fields = v.extracted_fields or []

        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if (c.status or "").upper() == "PASS")
        failed_checks = sum(1 for c in checks if (c.status or "").upper() == "FAIL")
        warning_checks = sum(1 for c in checks if (c.status or "").upper() in ["WARN", "WARNING"])

        extracted_dicts: List[Dict[str, Any]] = [
            {
                "field_name": f.field_name,
                "field_value": f.field_value,
                "confidence": f.confidence,
                "source_text": f.source_text,
            }
            for f in fields
        ]

        check_dicts: List[Dict[str, Any]] = [
            {
                "rule_code": c.rule_code,
                "rule_name": c.rule_name,
                "status": c.status,
                "severity": c.severity,
                "expected_value": c.expected_value,
                "actual_value": c.actual_value,
                "explanation": c.explanation,
            }
            for c in checks
        ]

        # Recommendations based on failed checks
        recs: List[str] = []
        for c in checks:
            if (c.status or "").upper() == "FAIL":
                recs.append(f"Remediate {c.rule_name} ({c.rule_code}): Ensure declaration '{c.expected_value}' is clearly printed on the primary display panel.")

        if not recs:
            recs.append("All evaluated statutory declarations comply with Legal Metrology (Packaged Commodities) Rules, 2011.")

        status_str = (v.verification_status or "COMPLIANT").upper()
        score_val = float(v.overall_score if v.overall_score is not None else 100.0)

        # Markdown Report Generation
        md_lines = [
            "# Legal Metrology Packaging Compliance Audit Report",
            "",
            f"**Verification Session ID**: `#{v.id}`  ",
            f"**Audit Timestamp**: `{v.completed_at or v.created_at or datetime.utcnow()}`  ",
            f"**Overall Compliance Status**: **{status_str}**  ",
            f"**Compliance Score**: **{score_val:.1f} / 100.0**  ",
            "",
            "---",
            "",
            "## 1. Product Identity",
            f"- **Product Name**: {prod_name}",
            f"- **Brand**: {brand_name or 'N/A'}",
            f"- **Manufacturer**: {v.product.manufacturer_name if v.product else 'N/A'}",
            f"- **Net Quantity**: {v.product.net_quantity if v.product else 'N/A'} {v.product.unit if v.product and v.product.unit else ''}",
            f"- **MRP**: Rs. {v.product.mrp:.2f}" if v.product and v.product.mrp else "- **MRP**: Not declared",
            f"- **Country of Origin**: {v.product.country_of_origin if v.product else 'N/A'}",
            f"- **Batch No.**: {v.product.batch_number if v.product else 'N/A'}",
            f"- **Date of Mfg**: {v.product.date_of_manufacture if v.product else 'N/A'}",
            "",
            "## 2. Regulatory Evaluation Summary",
            f"- **Total Checks Evaluated**: {total_checks}",
            f"- **Passed Checks**: {passed_checks}",
            f"- **Failed Checks / Violations**: {failed_checks}",
            f"- **Warnings**: {warning_checks}",
            "",
            "| Rule Code | Rule Description | Severity | Status | Actual Value |",
            "|:---|:---|:---|:---|:---|",
        ]

        for c in checks:
            md_lines.append(
                f"| `{c.rule_code}` | {c.rule_name} | {c.severity or 'MEDIUM'} | **{c.status}** | {c.actual_value or 'Missing'} |"
            )

        md_lines.extend([
            "",
            "## 3. Statutory Remediation Recommendations",
        ])
        for r in recs:
            md_lines.append(f"- {r}")

        md_lines.extend([
            "",
            "---",
            "*Report generated by AI-Powered Packaged Product Compliance Verification System.*",
        ])

        markdown_content = "\n".join(md_lines)
        summary_text = (
            f"Verification #{v.id} for '{prod_name}' completed with status {status_str} "
            f"and compliance score {score_val:.1f}/100 ({passed_checks}/{total_checks} rules passed)."
        )

        return VerificationReportResponse(
            verification_id=v.id,
            product_id=v.product_id,
            product_name=prod_name,
            brand_name=brand_name,
            overall_status=status_str,
            overall_score=score_val,
            verified_at=v.completed_at or v.created_at,
            summary=summary_text,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warning_checks=warning_checks,
            extracted_fields=extracted_dicts,
            compliance_checks=check_dicts,
            recommendations=recs,
            markdown_report=markdown_content,
        )
