from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from services.extraction_service.parser import (
    parse_mrp,
    parse_net_quantity,
    parse_date_of_manufacture,
    parse_expiry_date,
    parse_date_of_import,
    parse_batch_number,
    parse_country_of_origin,
    parse_manufacturer,
    parse_importer,
    parse_customer_care,
    parse_fssai,
    parse_ingredients,
    parse_allergens,
    parse_storage_instructions,
    parse_brand_and_product_name,
)
from backend.utils.logger import logger


@dataclass
class ExtractedFieldData:
    """
    Representation of an individual extracted product declaration.
    """
    field_name: str
    value: Any
    unit: Optional[str] = None
    raw_value: Optional[str] = None
    source_text: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "field_name": self.field_name,
            "value": self.value,
            "raw_value": self.raw_value,
            "source_text": self.source_text,
            "confidence": round(self.confidence, 4),
        }
        if self.unit is not None:
            d["unit"] = self.unit
        return d


@dataclass
class ExtractionResult:
    """
    Structured outcome of the NLP & rule-based extraction pipeline.
    """
    success: bool
    fields: List[ExtractedFieldData] = field(default_factory=list)
    field_count: int = 0
    average_confidence: float = 0.0
    raw_text: Optional[str] = None

    def get_field(self, field_name: str) -> Optional[ExtractedFieldData]:
        for f in self.fields:
            if f.field_name == field_name:
                return f
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "fields": [f.to_dict() for f in self.fields],
            "field_count": len(self.fields),
            "average_confidence": round(self.average_confidence, 4),
            "raw_text": self.raw_text,
        }


class ProductFieldExtractor:
    """
    Orchestration engine for regex, rule-based, and lightweight NLP extraction.
    """

    @classmethod
    def extract_from_text(cls, raw_text: str) -> ExtractionResult:
        """
        Extracts all identifiable Legal Metrology and packaged product fields from raw OCR text.
        """
        if not raw_text or not raw_text.strip():
            return ExtractionResult(
                success=True,
                fields=[],
                field_count=0,
                average_confidence=0.0,
                raw_text="",
            )

        text = raw_text.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        extracted: List[ExtractedFieldData] = []

        # 1. Header heuristics: Brand and Product Name
        brand_item, product_item = parse_brand_and_product_name(lines)
        if brand_item:
            extracted.append(ExtractedFieldData(**brand_item))
        if product_item:
            extracted.append(ExtractedFieldData(**product_item))

        # 2. Net Quantity & Unit
        qty_item = parse_net_quantity(text)
        if qty_item:
            extracted.append(ExtractedFieldData(**qty_item))

        # 3. Maximum Retail Price (MRP)
        mrp_item = parse_mrp(text)
        if mrp_item:
            extracted.append(ExtractedFieldData(**mrp_item))

        # 4. Date of Manufacture
        mfd_item = parse_date_of_manufacture(text)
        if mfd_item:
            extracted.append(ExtractedFieldData(**mfd_item))

        # 5. Expiry / Use By Date
        exp_item = parse_expiry_date(text)
        if exp_item:
            extracted.append(ExtractedFieldData(**exp_item))

        # 6. Date of Import
        import_item = parse_date_of_import(text)
        if import_item:
            extracted.append(ExtractedFieldData(**import_item))

        # 7. Batch Number
        batch_item = parse_batch_number(text)
        if batch_item:
            extracted.append(ExtractedFieldData(**batch_item))

        # 8. Country of Origin
        origin_item = parse_country_of_origin(text)
        if origin_item:
            extracted.append(ExtractedFieldData(**origin_item))

        # 9. Manufacturer Details
        mfg_item = parse_manufacturer(text)
        if mfg_item:
            extracted.append(ExtractedFieldData(**mfg_item))

        # 10. Importer Details
        imp_item = parse_importer(text)
        if imp_item:
            extracted.append(ExtractedFieldData(**imp_item))

        # 11. Customer Care Details
        care_item = parse_customer_care(text)
        if care_item:
            extracted.append(ExtractedFieldData(**care_item))

        # 12. FSSAI / Food License Number
        fssai_item = parse_fssai(text)
        if fssai_item:
            extracted.append(ExtractedFieldData(**fssai_item))

        # 13. Ingredients
        ing_item = parse_ingredients(text)
        if ing_item:
            extracted.append(ExtractedFieldData(**ing_item))

        # 14. Allergen Information
        allergen_item = parse_allergens(text)
        if allergen_item:
            extracted.append(ExtractedFieldData(**allergen_item))

        # 15. Storage Instructions
        storage_item = parse_storage_instructions(text)
        if storage_item:
            extracted.append(ExtractedFieldData(**storage_item))

        # Calculate average confidence
        total_conf = sum(f.confidence for f in extracted)
        avg_conf = (total_conf / len(extracted)) if extracted else 0.0

        return ExtractionResult(
            success=True,
            fields=extracted,
            field_count=len(extracted),
            average_confidence=round(avg_conf, 4),
            raw_text=text,
        )


def extract_product_fields(text: str) -> ExtractionResult:
    """
    Convenience functional interface for product field extraction.
    """
    return ProductFieldExtractor.extract_from_text(text)
