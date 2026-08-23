import json
import re
from typing import Any, Dict, List, Optional
from backend.config import get_settings
from backend.utils.logger import logger
from services.explanation_service.models import (
    ExplanationContext,
    GeneratedExplanationItem,
    ExplanationResult,
)
from services.explanation_service.prompt import SYSTEM_PROMPT, build_user_prompt
from services.explanation_service.recommendation import get_deterministic_explanation


class LLMExplanationService:
    """
    Provider-independent LLM service for evidence-grounded legal explanation generation.
    Supports graceful fallback and safe error handling.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = None,
    ):
        settings = get_settings()
        self.provider = (provider or settings.LLM_PROVIDER or "mock").lower()
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL or "gemini-1.5-flash"
        self.timeout = timeout or settings.LLM_TIMEOUT or 10.0
        self.temperature = temperature or settings.LLM_TEMPERATURE or 0.1

    def generate_explanation(self, context: ExplanationContext) -> Optional[ExplanationResult]:
        """
        Invokes configured LLM provider to produce legal explanations.
        Returns ExplanationResult if successful, or None on failure to trigger fallback.
        """
        if self.provider == "mock":
            return self._generate_mock_explanation(context)

        if not self.api_key or not self.api_key.strip():
            logger.info("No LLM API key configured; falling back to deterministic explanation engine.")
            return None

        try:
            if self.provider == "gemini":
                return self._call_gemini(context)
            elif self.provider in {"openai", "chatgpt"}:
                return self._call_openai(context)
            else:
                logger.warning(f"Unsupported LLM provider '{self.provider}'. Engaging deterministic fallback.")
                return None
        except Exception as e:
            logger.warning(f"LLM explanation request failed: {type(e).__name__} - {str(e)}. Engaging deterministic fallback.")
            return None

    def _generate_mock_explanation(self, context: ExplanationContext) -> ExplanationResult:
        """
        Generates simulated LLM explanation with rich legal explanations for offline/test environments.
        """
        explanations: List[GeneratedExplanationItem] = []
        recommendations: List[str] = []

        for item in context.evidence_items:
            det = get_deterministic_explanation(item)
            explanations.append(
                GeneratedExplanationItem(
                    rule_code=det.rule_code,
                    rule_name=det.rule_name,
                    severity=det.severity,
                    status=det.status,
                    explanation=f"{det.explanation} (Verified against Legal Metrology Rule 6)",
                    why_it_matters=det.why_it_matters,
                    recommended_action=det.recommended_action,
                    evidence=det.evidence,
                    confidence=0.96,
                )
            )
            if item.status.upper() in {"FAIL", "WARN"}:
                if det.recommended_action not in recommendations:
                    recommendations.append(det.recommended_action)

        if not recommendations:
            recommendations.append("All statutory packaging declarations meet verified standards.")

        failed_count = sum(1 for item in context.evidence_items if item.status.upper() == "FAIL")
        if context.overall_status.upper() == "COMPLIANT":
            summary = (
                f"Statutory verification complete: Product is COMPLIANT with an overall score of {context.overall_score:.1f}/100. "
                "All evaluated mandatory packaging declarations are present."
            )
        elif context.overall_status.upper() == "PARTIALLY_COMPLIANT":
            summary = (
                f"Statutory verification complete: Product is PARTIALLY COMPLIANT ({context.overall_score:.1f}/100). "
                f"Identified {failed_count} non-compliant declaration(s) requiring remediation."
            )
        else:
            summary = (
                f"Statutory verification complete: Product is NON_COMPLIANT ({context.overall_score:.1f}/100). "
                f"Multiple critical statutory declarations failed inspection."
            )

        return ExplanationResult(
            overall_status=context.overall_status,
            overall_score=context.overall_score,
            summary=summary,
            explanations=explanations,
            recommendations=recommendations,
            ai_generated=True,
            error_message=None,
        )

    def _call_gemini(self, context: ExplanationContext) -> Optional[ExplanationResult]:
        """Calls Google Gemini API using google-generativeai or raw HTTP request."""
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=SYSTEM_PROMPT,
                generation_config={"temperature": self.temperature, "response_mime_type": "application/json"},
            )
            prompt = build_user_prompt(context)
            response = model.generate_content(prompt, request_options={"timeout": self.timeout})
            return self._parse_llm_json_response(response.text, context)
        except ImportError:
            logger.warning("google-generativeai package not installed; skipping Gemini call.")
            return None

    def _call_openai(self, context: ExplanationContext) -> Optional[ExplanationResult]:
        """Calls OpenAI Chat Completion API."""
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI(api_key=self.api_key, timeout=self.timeout)
            prompt = build_user_prompt(context)
            response = client.chat.completions.create(
                model=self.model or "gpt-4o-mini",
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            return self._parse_llm_json_response(content, context)
        except ImportError:
            logger.warning("openai package not installed; skipping OpenAI call.")
            return None

    def _parse_llm_json_response(self, text: str, context: ExplanationContext) -> Optional[ExplanationResult]:
        """
        Safely parses and validates structured JSON from LLM response.
        Enforces evidence grounding and preserves authoritative status/scores.
        """
        if not text or not text.strip():
            return None

        # Clean markdown codeblocks if present
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        data = json.loads(clean_text)
        summary = data.get("summary", "")
        recommendations = data.get("recommendations", [])
        raw_explanations = data.get("explanations", [])

        # Build map of expected evidence items by rule_code to prevent hallucinated rule codes
        evidence_by_code = {item.rule_code: item for item in context.evidence_items}
        validated_explanations: List[GeneratedExplanationItem] = []

        for exp in raw_explanations:
            code = exp.get("rule_code")
            if code in evidence_by_code:
                orig_item = evidence_by_code[code]
                validated_explanations.append(
                    GeneratedExplanationItem(
                        rule_code=orig_item.rule_code,
                        rule_name=orig_item.rule_name,
                        severity=orig_item.severity,
                        status=orig_item.status,
                        explanation=exp.get("explanation") or exp.get("why_it_matters", ""),
                        why_it_matters=exp.get("why_it_matters", ""),
                        recommended_action=exp.get("recommended_action", ""),
                        evidence=exp.get("evidence", f"Actual: {orig_item.actual_value}"),
                        confidence=float(exp.get("confidence", 0.95)),
                    )
                )

        # Fallback for any missing checks from the LLM response
        for item in context.evidence_items:
            if item.rule_code not in [ve.rule_code for ve in validated_explanations]:
                validated_explanations.append(get_deterministic_explanation(item))

        return ExplanationResult(
            overall_status=context.overall_status,
            overall_score=context.overall_score,
            summary=summary or f"Verification results: {context.overall_status}",
            explanations=validated_explanations,
            recommendations=recommendations or ["Review package declarations against Legal Metrology guidelines."],
            ai_generated=True,
            error_message=None,
        )
