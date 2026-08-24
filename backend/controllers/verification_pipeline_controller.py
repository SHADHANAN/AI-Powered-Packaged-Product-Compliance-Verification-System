from typing import Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.schemas.pipeline import (
    VerificationPipelineResponse,
    PipelineOCRSummary,
    PipelineExtractedFieldItem,
    PipelineComplianceCheckItem,
    PipelineExplanationItem,
    PipelineExplanationSummary,
)
from services.verification_service.pipeline import VerificationPipeline
from backend.utils.logger import logger


class VerificationPipelineController:
    """
    Controller handling end-to-end verification pipeline requests (POST /api/verify).
    """

    @classmethod
    async def verify_image(
        cls,
        db: Session,
        image: UploadFile,
        preprocessing_strategy: Optional[str] = "standard",
    ) -> VerificationPipelineResponse:
        """
        Processes an uploaded package image through the entire compliance pipeline.
        """
        if not image or not image.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing image file in multipart upload request.",
            )

        # MIME validation
        from services.ocr_service.image_utils import is_valid_mime_type, sanitize_filename
        if image.content_type and not is_valid_mime_type(image.content_type):
            logger.warning(f"Rejected invalid MIME type: {image.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file MIME type '{image.content_type}'. Please upload an image file (JPEG, PNG, WEBP, BMP, TIFF).",
            )

        clean_filename = sanitize_filename(image.filename)

        try:
            image_bytes = await image.read()
        except Exception as e:
            logger.error(f"Failed to read image stream: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to read uploaded image stream: {str(e)}",
            )

        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image file is empty (0 bytes).",
            )

        # Run pipeline
        pipeline_result = VerificationPipeline.run(
            db=db,
            image_bytes=image_bytes,
            filename=clean_filename,
            preprocessing_strategy=preprocessing_strategy or "standard",
        )

        if not pipeline_result.success:
            # If image validation failed specifically, return 400
            if not pipeline_result.stages.image_validation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=pipeline_result.error_message or "Invalid image file.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=pipeline_result.error_message or "Verification pipeline failed.",
                )

        # Map pipeline result to response schema
        ocr_summary = None
        if pipeline_result.ocr:
            ocr_summary = PipelineOCRSummary(
                text=pipeline_result.ocr.get("text", ""),
                average_confidence=float(pipeline_result.ocr.get("average_confidence", 0.0)),
                line_count=int(pipeline_result.ocr.get("line_count", 0)),
            )

        extracted_items = [
            PipelineExtractedFieldItem(
                field_name=f.get("field_name", ""),
                field_value=f.get("field_value"),
                unit=f.get("unit"),
                confidence=float(f.get("confidence", 0.0)),
                source_text=f.get("source_text"),
            )
            for f in pipeline_result.extracted_fields
        ]

        compliance_items = [
            PipelineComplianceCheckItem(
                rule_code=c.get("rule_code", ""),
                rule_name=c.get("rule_name", ""),
                status=c.get("status", ""),
                severity=c.get("severity", ""),
                expected_value=c.get("expected_value"),
                actual_value=c.get("actual_value"),
                explanation=c.get("explanation"),
            )
            for c in pipeline_result.compliance_checks
        ]

        explanation_summary = None
        if pipeline_result.explanation:
            exp_data = pipeline_result.explanation
            exp_items = [
                PipelineExplanationItem(
                    rule_code=item.get("rule_code", ""),
                    rule_name=item.get("rule_name", ""),
                    severity=item.get("severity", "MEDIUM"),
                    status=item.get("status", ""),
                    explanation=item.get("explanation", ""),
                    why_it_matters=item.get("why_it_matters", ""),
                    recommended_action=item.get("recommended_action", ""),
                    evidence=item.get("evidence", ""),
                    confidence=float(item.get("confidence", 0.95)),
                )
                for item in exp_data.get("items", [])
            ]
            explanation_summary = PipelineExplanationSummary(
                summary=exp_data.get("summary", ""),
                items=exp_items,
                recommendations=exp_data.get("recommendations", []),
                ai_generated=bool(exp_data.get("ai_generated", False)),
            )

        return VerificationPipelineResponse(
            success=True,
            verification_id=pipeline_result.verification_id,
            product_id=pipeline_result.product_id,
            overall_status=pipeline_result.overall_status,
            overall_score=pipeline_result.overall_score,
            ocr=ocr_summary,
            extracted_fields=extracted_items,
            compliance_checks=compliance_items,
            explanation=explanation_summary,
            error_message=None,
        )
