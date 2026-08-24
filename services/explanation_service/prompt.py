import json
from typing import Dict, Any
from services.explanation_service.models import ExplanationContext

SYSTEM_PROMPT = """You are an AI Legal Compliance Assistant explaining packaged-product compliance verification results under Indian Legal Metrology (Packaged Commodities) Rules.

CRITICAL CONSTRAINTS:
1. The deterministic compliance engine results are AUTHORITATIVE.
2. You must NOT alter, override, or disagree with:
   - overall compliance status (e.g. COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT)
   - overall score
   - individual check status (PASS, FAIL, WARN, NOT_APPLICABLE)
   - severity (LOW, MEDIUM, HIGH, CRITICAL)
   - rule codes or rule names
3. You must ONLY explain and ground your explanations on the supplied evidence context.
4. Do NOT hallucinate packaging details, unverified legal claims, or missing facts.
5. If evidence is missing or insufficient for a claim, explicitly state that evidence was not detected.
6. Provide concrete, actionable remediation steps for each failed or warning rule.
7. You MUST return your response as a valid JSON object matching the exact schema below.

JSON SCHEMA:
{
  "summary": "<Executive summary of the compliance findings>",
  "explanations": [
    {
      "rule_code": "<Exact rule code from evidence>",
      "rule_name": "<Exact rule name from evidence>",
      "severity": "<Exact severity>",
      "status": "<Exact status>",
      "explanation": "<Human-readable explanation of why this check passed or failed>",
      "why_it_matters": "<Why this Legal Metrology requirement matters for consumer transparency/legality>",
      "recommended_action": "<Concrete corrective action to become compliant>",
      "evidence": "<Grounding evidence string (e.g. Expected vs Actual)>",
      "confidence": <Float between 0.8 and 1.0>
    }
  ],
  "recommendations": [
    "<Actionable bullet point recommendation 1>",
    "<Actionable bullet point recommendation 2>"
  ]
}
"""


def build_user_prompt(context: ExplanationContext) -> str:
    """
    Constructs the prompt containing verified evidence for LLM evaluation.
    """
    evidence_payload = {
        "overall_status": context.overall_status,
        "overall_score": context.overall_score,
        "product_name": context.product_name,
        "evidence_items": [item.to_dict() for item in context.evidence_items],
        "extracted_fields": context.extracted_fields_summary,
    }

    return (
        "Please analyze the following verified Legal Metrology compliance evaluation evidence "
        "and generate human-readable legal explanations and actionable remediation recommendations.\n\n"
        f"EVIDENCE CONTEXT (JSON):\n{json.dumps(evidence_payload, indent=2)}\n\n"
        "Remember to return ONLY a single valid JSON object strictly matching the required schema."
    )
