import re
from typing import Dict, List, Optional, Tuple, Any
from services.extraction_service.regex_patterns import (
    MRP_PATTERNS,
    QUANTITY_PATTERNS,
    MFD_PATTERNS,
    EXPIRY_PATTERNS,
    IMPORT_DATE_PATTERNS,
    BATCH_PATTERNS,
    ORIGIN_PATTERNS,
    MANUFACTURER_PATTERNS,
    IMPORTER_PATTERNS,
    CUSTOMER_CARE_PATTERNS,
    FSSAI_PATTERNS,
    INGREDIENTS_PATTERNS,
    ALLERGEN_PATTERNS,
    STORAGE_PATTERNS,
)
from services.extraction_service.nlp import (
    clean_text,
    clean_price,
    clean_quantity,
    normalize_unit,
    extract_emails_and_phones,
)

# Common declaration prefixes used to exclude lines from brand/product name candidates
DECLARATION_KEYWORDS = [
    "MRP", "M.R.P", "PRICE", "MAXIMUM RETAIL",
    "NET QTY", "NET WT", "NET CONTENT", "NET QUANTITY", "NET WEIGHT", "NET",
    "MFD", "MFG", "MANUFACTURED", "PKD", "PACKED", "DATE OF",
    "EXP", "EXPIRY", "USE BY", "BEST BEFORE", "VALID UPTO",
    "BATCH", "LOT", "B. NO", "B.NO",
    "MFD BY", "MFD. BY", "MFG BY", "MANUFACTURED BY", "PACKED BY", "MKTG BY", "MARKETED BY",
    "IMPORTED BY", "IMPORTER",
    "COUNTRY OF ORIGIN", "MADE IN", "PRODUCT OF",
    "CUSTOMER CARE", "CONSUMER CARE", "FEEDBACK", "TOLL FREE", "HELPLINE",
    "INGREDIENTS", "ALLERGEN", "CONTAINS", "STORAGE", "STORE IN",
    "FSSAI", "LIC NO", "PROPRIETARY FOOD",
]


def _find_pattern_match(patterns: List[re.Pattern], text: str) -> Optional[Tuple[re.Match, str]]:
    """Helper to test a list of patterns against full text or line-by-line."""
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            # Extract matched line as source text
            start = text.rfind("\n", 0, match.start())
            start = 0 if start == -1 else start + 1
            end = text.find("\n", match.end())
            end = len(text) if end == -1 else end
            source_line = text[start:end].strip()
            return match, source_line
    return None


def parse_mrp(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(MRP_PATTERNS, text)
    if result:
        match, source_line = result
        raw_val = match.group(1)
        val = clean_price(raw_val)
        if val is not None and val > 0:
            return {
                "field_name": "mrp",
                "value": val,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.98 if "MRP" in source_line.upper() or "PRICE" in source_line.upper() else 0.85,
            }
    return None


def parse_net_quantity(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(QUANTITY_PATTERNS, text)
    if result:
        match, source_line = result
        raw_qty = match.group(1)
        raw_unit = match.group(2)
        val = clean_quantity(raw_qty)
        unit = normalize_unit(raw_unit)
        if val is not None and unit:
            confidence = 0.98 if "NET" in source_line.upper() or "QTY" in source_line.upper() or "WT" in source_line.upper() else 0.85
            return {
                "field_name": "net_quantity",
                "value": val,
                "unit": unit,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": confidence,
            }
    return None


def parse_date_of_manufacture(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(MFD_PATTERNS, text)
    if result:
        match, source_line = result
        date_str = clean_text(match.group(1))
        if date_str:
            return {
                "field_name": "date_of_manufacture",
                "value": date_str,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.95,
            }
    return None


def parse_expiry_date(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(EXPIRY_PATTERNS, text)
    if result:
        match, source_line = result
        date_str = clean_text(match.group(1))
        if date_str:
            return {
                "field_name": "expiry_date",
                "value": date_str,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.95,
            }
    return None


def parse_date_of_import(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(IMPORT_DATE_PATTERNS, text)
    if result:
        match, source_line = result
        date_str = clean_text(match.group(1))
        if date_str:
            return {
                "field_name": "date_of_import",
                "value": date_str,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.92,
            }
    return None


def parse_batch_number(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(BATCH_PATTERNS, text)
    if result:
        match, source_line = result
        batch_str = clean_text(match.group(1))
        if batch_str:
            return {
                "field_name": "batch_number",
                "value": batch_str,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.96,
            }
    return None


def parse_country_of_origin(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(ORIGIN_PATTERNS, text)
    if result:
        match, source_line = result
        raw_matched = match.group(1).split("\n")[0].strip()
        country_raw = clean_text(raw_matched)
        if country_raw:
            # Capitalize country words and filter noise words
            words = [word.capitalize() for word in country_raw.split() if word.lower() not in {"of", "the", "in", "country", "origin"}]
            country_clean = " ".join(words)
            if country_clean:
                return {
                    "field_name": "country_of_origin",
                    "value": country_clean,
                    "raw_value": match.group(0).strip(),
                    "source_text": source_line,
                    "confidence": 0.97,
                }
    return None


def parse_manufacturer(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(MANUFACTURER_PATTERNS, text)
    if result:
        match, source_line = result
        mfg_text = clean_text(match.group(1))
        # If the matched line was just the prefix (e.g. "MFD. & MKTG. BY:"), check the immediate next line in text
        if (not mfg_text or len(mfg_text) < 3) and "\n" in text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for idx, line in enumerate(lines):
                if line == source_line and idx + 1 < len(lines):
                    mfg_text = lines[idx + 1]
                    source_line = f"{source_line}\n{mfg_text}"
                    break

        if mfg_text:
            return {
                "field_name": "manufacturer_name",
                "value": mfg_text,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.92,
            }
    return None


def parse_importer(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(IMPORTER_PATTERNS, text)
    if result:
        match, source_line = result
        imp_text = clean_text(match.group(1))
        if (not imp_text or len(imp_text) < 3) and "\n" in text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for idx, line in enumerate(lines):
                if line == source_line and idx + 1 < len(lines):
                    imp_text = lines[idx + 1]
                    source_line = f"{source_line}\n{imp_text}"
                    break

        if imp_text:
            return {
                "field_name": "importer_name",
                "value": imp_text,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.90,
            }
    return None


def parse_customer_care(text: str) -> Optional[Dict[str, Any]]:
    phones, emails = extract_emails_and_phones(text)
    care_match = _find_pattern_match(CUSTOMER_CARE_PATTERNS, text)

    contact_parts = []
    if phones:
        contact_parts.extend(phones)
    if emails:
        contact_parts.extend(emails)

    if care_match:
        match, source_line = care_match
        care_details = clean_text(match.group(1))
        if care_details and care_details not in contact_parts:
            contact_parts.insert(0, care_details)
        full_value = ", ".join(dict.fromkeys(contact_parts)) if contact_parts else care_details
        return {
            "field_name": "customer_care_details",
            "value": full_value,
            "raw_value": match.group(0).strip(),
            "source_text": source_line,
            "confidence": 0.94,
        }
    elif contact_parts:
        return {
            "field_name": "customer_care_details",
            "value": ", ".join(dict.fromkeys(contact_parts)),
            "raw_value": ", ".join(contact_parts),
            "source_text": ", ".join(contact_parts),
            "confidence": 0.88,
        }
    return None


def parse_fssai(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(FSSAI_PATTERNS, text)
    if result:
        match, source_line = result
        lic_no = clean_text(match.group(1))
        if lic_no:
            return {
                "field_name": "food_license_number",
                "value": lic_no,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.96,
            }
    return None


def parse_ingredients(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(INGREDIENTS_PATTERNS, text)
    if result:
        match, source_line = result
        ing_text = clean_text(match.group(1))
        if ing_text:
            return {
                "field_name": "ingredients",
                "value": ing_text,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.90,
            }
    return None


def parse_allergens(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(ALLERGEN_PATTERNS, text)
    if result:
        match, source_line = result
        allergen_text = clean_text(match.group(1))
        if allergen_text:
            return {
                "field_name": "allergen_information",
                "value": allergen_text,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.88,
            }
    return None


def parse_storage_instructions(text: str) -> Optional[Dict[str, Any]]:
    result = _find_pattern_match(STORAGE_PATTERNS, text)
    if result:
        match, source_line = result
        storage_text = clean_text(match.group(1))
        if storage_text:
            return {
                "field_name": "storage_instructions",
                "value": storage_text,
                "raw_value": match.group(0).strip(),
                "source_text": source_line,
                "confidence": 0.85,
            }
    return None


def parse_brand_and_product_name(lines: List[str]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Contextual heuristic parser to identify Brand Name and Product Name
    from header / prominent lines, filtering out known declaration lines.
    """
    candidates = []
    for line in lines:
        cleaned = clean_text(line)
        if not cleaned or len(cleaned) < 2:
            continue

        # Check if line contains any known declaration keyword
        upper_line = cleaned.upper()
        if any(kw in upper_line for kw in DECLARATION_KEYWORDS):
            continue

        # Ignore purely numerical or symbol lines
        if re.match(r"^[\d\W_]+$", cleaned):
            continue

        candidates.append(cleaned)

    brand_result = None
    product_result = None

    if candidates:
        # First candidate is typically Brand or Product Name
        first_candidate = candidates[0]

        if len(candidates) >= 2:
            brand_result = {
                "field_name": "brand_name",
                "value": first_candidate,
                "raw_value": first_candidate,
                "source_text": first_candidate,
                "confidence": 0.88,
            }
            # Combine second and possibly third candidate for full product flavor/name
            second_candidate = candidates[1]
            if len(candidates) >= 3 and len(candidates[2].split()) <= 3 and not candidates[2].isupper():
                product_name_val = f"{second_candidate} {candidates[2]}"
            else:
                product_name_val = second_candidate

            product_result = {
                "field_name": "product_name",
                "value": product_name_val,
                "raw_value": product_name_val,
                "source_text": product_name_val,
                "confidence": 0.85,
            }
        else:
            # Single candidate found
            product_result = {
                "field_name": "product_name",
                "value": first_candidate,
                "raw_value": first_candidate,
                "source_text": first_candidate,
                "confidence": 0.75,
            }

    return brand_result, product_result
