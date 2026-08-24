from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck
from backend.utils.logger import logger
from services.ocr_service.ocr import PaddleOCRService
from services.ocr_service.image_utils import validate_image_bytes
from services.extraction_service.extractor import extract_product_fields
from services.compliance_service.rule_engine import RuleEngine
from services.explanation_service.evidence import build_evidence_context
from services.explanation_service.report import ExplanationReportGenerator
from services.explanation_service.llm import LLMExplanationService
from services.verification_service.models import VerificationPipelineResult, PipelineStageStatus


class VerificationPipeline:
    """
    End-to-end packaged product compliance verification pipeline orchestrator.
    Executes OCR -> NLP Extraction -> DB Persistence -> RuleEngine -> AI Explanation.
    """

    @classmethod
    def run(
        cls,
        db: Session,
        image_bytes: bytes,
        filename: str,
        preprocessing_strategy: str = "standard",
        llm_service: Optional[LLMExplanationService] = None,
    ) -> VerificationPipelineResult:
        """
        Executes the complete end-to-end verification pipeline.
        """
        stages = PipelineStageStatus()

        # Step 1: Image Validation
        is_valid, err_msg, _ = validate_image_bytes(image_bytes, filename)
        if not is_valid:
            logger.warning(f"Image validation failed for '{filename}': {err_msg}")
            return VerificationPipelineResult(
                success=False,
                overall_status="ERROR",
                error_message=f"Image validation failed: {err_msg}",
                stages=stages,
            )
        stages.image_validation = True

        # Step 2: OCR Recognition
        try:
            from services.ocr_service.ocr import get_ocr_service
            ocr_service = get_ocr_service()
            ocr_res = ocr_service.extract_text(
                image_input=image_bytes,
                preprocess=True,
                strategy=preprocessing_strategy,
            )
            ocr_text = ocr_res.text or ""
            ocr_summary = {
                "text": ocr_text,
                "average_confidence": round(ocr_res.average_confidence, 4),
                "line_count": len(ocr_res.lines),
            }
            stages.ocr = True
        except Exception as e:
            logger.exception(f"OCR recognition stage failed: {e}")
            return VerificationPipelineResult(
                success=False,
                overall_status="ERROR",
                error_message=f"OCR recognition error: {str(e)}",
                stages=stages,
            )

        # Step 3: NLP Field Extraction & Normalization
        try:
            extraction_res = extract_product_fields(ocr_text)
            extracted_fields_list: List[Dict[str, Any]] = [
                {
                    "field_name": f.field_name,
                    "field_value": str(f.value) if f.value is not None else None,
                    "unit": f.unit,
                    "confidence": f.confidence,
                    "source_text": f.source_text,
                }
                for f in extraction_res.fields
            ]
            stages.extraction = True
        except Exception as e:
            logger.exception(f"Field extraction stage failed: {e}")
            return VerificationPipelineResult(
                success=False,
                overall_status="ERROR",
                ocr=ocr_summary,
                error_message=f"Field extraction error: {str(e)}",
                stages=stages,
            )

        # Helper to retrieve normalized field value
        def get_field_val(name: str) -> Optional[Any]:
            f = extraction_res.get_field(name)
            return f.value if f else None

        # Step 4 & 5: Create Product & Verification in Database
        try:
            mrp_val = get_field_val("mrp")
            numeric_mrp = None
            if mrp_val is not None:
                try:
                    numeric_mrp = float(mrp_val)
                except (ValueError, TypeError):
                    pass

            product = Product(
                product_name=str(get_field_val("product_name") or "Unidentified Product"),
                brand_name=get_field_val("brand_name"),
                manufacturer_name=get_field_val("manufacturer_name"),
                importer_name=get_field_val("importer_name"),
                country_of_origin=get_field_val("country_of_origin"),
                net_quantity=str(get_field_val("net_quantity")) if get_field_val("net_quantity") is not None else None,
                unit=get_field_val("unit"),
                mrp=numeric_mrp,
                batch_number=get_field_val("batch_number"),
                date_of_manufacture=get_field_val("date_of_manufacture"),
                date_of_import=get_field_val("date_of_import"),
                customer_care_details=get_field_val("customer_care_details"),
            )
            db.add(product)
            db.commit()
            db.refresh(product)

            verification = Verification(
                product_id=product.id,
                verification_status="processing",
                overall_score=0.0,
            )
            db.add(verification)
            db.commit()
            db.refresh(verification)

            # Step 6: Persist ExtractedField records
            for f in extraction_res.fields:
                db_field = ExtractedField(
                    verification_id=verification.id,
                    field_name=f.field_name,
                    field_value=str(f.value) if f.value is not None else "",
                    confidence=f.confidence,
                    source_text=f.source_text,
                )
                db.add(db_field)

            stages.database_persist = True

        except Exception as e:
            db.rollback()
            logger.exception(f"Database persistence stage failed: {e}")
            return VerificationPipelineResult(
                success=False,
                overall_status="ERROR",
                ocr=ocr_summary,
                extracted_fields=extracted_fields_list,
                error_message=f"Database persistence error: {str(e)}",
                stages=stages,
            )

        # Step 7: Deterministic Compliance Rule Engine
        try:
            compliance_summary = RuleEngine.evaluate_fields(extraction_res.fields)

            compliance_checks_list: List[Dict[str, Any]] = []
            for chk in compliance_summary.checks:
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
                compliance_checks_list.append(chk.to_dict())

            # Update Verification with authoritative results
            verification.verification_status = compliance_summary.status.lower()
            verification.overall_score = compliance_summary.overall_score
            verification.completed_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(verification)
            stages.compliance_evaluation = True

        except Exception as e:
            db.rollback()
            logger.exception(f"Compliance evaluation stage failed: {e}")
            return VerificationPipelineResult(
                success=False,
                verification_id=verification.id,
                product_id=product.id,
                overall_status="ERROR",
                ocr=ocr_summary,
                extracted_fields=extracted_fields_list,
                error_message=f"Compliance evaluation error: {str(e)}",
                stages=stages,
            )

        # Step 8 & 9: Evidence-Grounded AI Explanation & Remediation
        try:
            context = build_evidence_context(
                checks=compliance_summary.checks,
                overall_score=compliance_summary.overall_score,
                overall_status=compliance_summary.status,
                extracted_fields=extraction_res.fields,
                product_name=product.product_name,
            )
            report = ExplanationReportGenerator.generate_report(context, llm_service=llm_service)
            explanation_payload = {
                "summary": report.summary,
                "items": [item.to_dict() for item in report.explanations],
                "recommendations": report.recommendations,
                "ai_generated": report.ai_generated,
            }
            stages.explanation_generation = True
        except Exception as e:
            logger.warning(f"AI explanation generation error: {e}. Engaging fallback.")
            explanation_payload = {
                "summary": f"Verification completed with status: {compliance_summary.status}.",
                "items": [],
                "recommendations": ["Review product labeling against Legal Metrology guidelines."],
                "ai_generated": False,
            }

        return VerificationPipelineResult(
            success=True,
            verification_id=verification.id,
            product_id=product.id,
            overall_status=compliance_summary.status,
            overall_score=compliance_summary.overall_score,
            ocr=ocr_summary,
            extracted_fields=extracted_fields_list,
            compliance_checks=compliance_checks_list,
            explanation=explanation_payload,
            stages=stages,
            error_message=None,
        )
