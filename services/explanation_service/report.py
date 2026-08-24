from typing import Optional
from services.explanation_service.models import ExplanationContext, ExplanationResult
from services.explanation_service.llm import LLMExplanationService
from services.explanation_service.recommendation import generate_deterministic_result
from backend.utils.logger import logger


class ExplanationReportGenerator:
    """
    Orchestrates the generation of AI-powered legal explanations and remediation recommendations
    with seamless deterministic fallback.
    """

    @classmethod
    def generate_report(
        cls,
        context: ExplanationContext,
        llm_service: Optional[LLMExplanationService] = None,
    ) -> ExplanationResult:
        """
        Attempts LLM generation and safely falls back to deterministic rules on any failure.
        """
        service = llm_service or LLMExplanationService()

        try:
            result = service.generate_explanation(context)
            if result is not None:
                return result
        except Exception as e:
            logger.warning(f"Error during LLM explanation generation: {e}. Falling back to deterministic generator.")

        # Seamless deterministic fallback
        deterministic_res = generate_deterministic_result(context)
        return deterministic_res
