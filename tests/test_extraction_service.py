import pytest
from services.extraction_service.extractor import (
    ProductFieldExtractor,
    extract_product_fields,
)
from services.extraction_service.nlp import (
    normalize_unit,
    clean_price,
    clean_quantity,
)
from services.extraction_service.parser import (
    parse_mrp,
    parse_net_quantity,
    parse_date_of_manufacture,
    parse_expiry_date,
    parse_batch_number,
    parse_country_of_origin,
    parse_manufacturer,
    parse_importer,
    parse_customer_care,
)


def test_mrp_extraction_variations():
    """Test various MRP formats and currency symbols."""
    cases = [
        ("MRP Rs. 20.00", 20.0),
        ("MRP Rs 20", 20.0),
        ("M.R.P. ₹ 250.50", 250.5),
        ("MAXIMUM RETAIL PRICE: Rs. 149.00", 149.0),
        ("INCL OF ALL TAXES MRP Rs. 99", 99.0),
        ("Rs. 45.00 (INCL. OF ALL TAXES)", 45.0),
    ]
    for text, expected in cases:
        res = parse_mrp(text)
        assert res is not None, f"Failed to parse MRP from '{text}'"
        assert res["value"] == expected
        assert res["confidence"] >= 0.8
        assert res["source_text"] is not None


def test_net_quantity_and_unit_normalization():
    """Test net quantity extraction and unit canonicalization."""
    cases = [
        ("NET QTY 500 g", 500, "g"),
        ("NET WT 500g", 500, "g"),
        ("NET CONTENT: 1 kg", 1, "kg"),
        ("NET QUANTITY: 250 GMS", 250, "g"),
        ("NET VOLUME: 1.5 LITRES", 1.5, "l"),
        ("200 ml", 200, "ml"),
        ("NET QTY: 10 PCS", 10, "pcs"),
        ("1 L", 1, "l"),
    ]
    for text, expected_val, expected_unit in cases:
        res = parse_net_quantity(text)
        assert res is not None, f"Failed to parse quantity from '{text}'"
        assert res["value"] == expected_val
        assert res["unit"] == expected_unit
        assert res["confidence"] >= 0.8


def test_manufacturing_date_extraction():
    """Test MFD/MFG/PKD date formats."""
    cases = [
        ("MFD 12/05/2024", "12/05/2024"),
        ("MFG: 12-05-2024", "12-05-2024"),
        ("Manufactured on 15/08/2023", "15/08/2023"),
        ("DATE OF MANUFACTURE: 04/2024", "04/2024"),
        ("PKD. MAY 2024", "MAY 2024"),
    ]
    for text, expected in cases:
        res = parse_date_of_manufacture(text)
        assert res is not None, f"Failed to parse MFD from '{text}'"
        assert res["value"] == expected
        assert res["confidence"] >= 0.9


def test_expiry_and_use_by_extraction():
    """Test EXP/USE BY/BEST BEFORE formats."""
    cases = [
        ("USE BY 11/11/2024", "11/11/2024"),
        ("EXP: 11-11-2024", "11-11-2024"),
        ("EXPIRY DATE: 31/12/2025", "31/12/2025"),
        ("BEST BEFORE 6 MONTHS FROM MFG", "6 MONTHS FROM MFG"),
    ]
    for text, expected in cases:
        res = parse_expiry_date(text)
        assert res is not None, f"Failed to parse Expiry from '{text}'"
        assert res["value"] == expected
        assert res["confidence"] >= 0.9


def test_batch_number_extraction():
    """Test batch and lot number patterns."""
    cases = [
        ("BATCH NO. 24E1205", "24E1205"),
        ("BATCH: ABC123", "ABC123"),
        ("LOT NO ABC123", "ABC123"),
        ("B.NO: LOT-9988", "LOT-9988"),
    ]
    for text, expected in cases:
        res = parse_batch_number(text)
        assert res is not None, f"Failed to parse Batch from '{text}'"
        assert res["value"] == expected
        assert res["confidence"] >= 0.9


def test_country_of_origin_extraction():
    """Test country of origin declarations."""
    cases = [
        ("MADE IN INDIA", "India"),
        ("COUNTRY OF ORIGIN: INDIA", "India"),
        ("PRODUCT OF USA", "Usa"),
    ]
    for text, expected in cases:
        res = parse_country_of_origin(text)
        assert res is not None, f"Failed to parse Origin from '{text}'"
        assert res["value"] == expected
        assert res["confidence"] >= 0.9


def test_manufacturer_and_importer_extraction():
    """Test manufacturer and importer identification."""
    mfg_text = "MFD. & MKTG. BY: PepsiCo India Holdings Pvt. Ltd."
    mfg_res = parse_manufacturer(mfg_text)
    assert mfg_res is not None
    assert "PepsiCo India" in mfg_res["value"]

    imp_text = "IMPORTED BY: Global Trade Partners Pvt Ltd, Mumbai"
    imp_res = parse_importer(imp_text)
    assert imp_res is not None
    assert "Global Trade Partners" in imp_res["value"]


def test_customer_care_extraction():
    """Test customer care phone and email extraction."""
    care_text = "CUSTOMER CARE: 1800 22 4020, consumer.feedback@pepsico.com"
    care_res = parse_customer_care(care_text)
    assert care_res is not None
    assert "1800 22 4020" in care_res["value"]
    assert "consumer.feedback@pepsico.com" in care_res["value"]


def test_full_pipeline_sample_text():
    """Test full extraction pipeline on comprehensive packaged product label text."""
    sample_text = """LAY'S
Chile Limón
Flavour
PROPRIETARY FOOD - POTATO CHIPS
NET QTY 50 g
MRP Rs. 20.00
MFD 12/05/2024
USE BY 11/11/2024
BATCH NO. 24E1205
MFD. & MKTG. BY: PepsiCo India Holdings Pvt. Ltd.
MADE IN INDIA
CUSTOMER CARE: 1800 22 4020, consumer.feedback@pepsico.com
FSSAI LIC NO: 10014064000435
INGREDIENTS: Potatoes, Edible Vegetable Oil, Seasoning
ALLERGEN: Contains Milk
STORAGE: Store in a cool and dry place
"""
    result = extract_product_fields(sample_text)
    assert result.success is True
    assert result.field_count >= 10
    assert result.average_confidence >= 0.85

    # Check key fields
    brand = result.get_field("brand_name")
    assert brand is not None and "LAY'S" in brand.value

    product = result.get_field("product_name")
    assert product is not None and "Chile Limón" in product.value

    mrp = result.get_field("mrp")
    assert mrp is not None and mrp.value == 20.0
    assert mrp.source_text == "MRP Rs. 20.00"

    qty = result.get_field("net_quantity")
    assert qty is not None and qty.value == 50 and qty.unit == "g"

    mfd = result.get_field("date_of_manufacture")
    assert mfd is not None and mfd.value == "12/05/2024"

    exp = result.get_field("expiry_date")
    assert exp is not None and exp.value == "11/11/2024"

    batch = result.get_field("batch_number")
    assert batch is not None and batch.value == "24E1205"

    origin = result.get_field("country_of_origin")
    assert origin is not None and origin.value == "India"

    mfg = result.get_field("manufacturer_name")
    assert mfg is not None and "PepsiCo India" in mfg.value

    fssai = result.get_field("food_license_number")
    assert fssai is not None and fssai.value == "10014064000435"


def test_empty_and_garbage_text():
    """Test handling of empty and unstructured noise text."""
    empty_res = extract_product_fields("")
    assert empty_res.success is True
    assert empty_res.field_count == 0

    garbage_text = "!@#$%^&*()_+ random non-label gibberish words nothing structured 12345"
    garbage_res = extract_product_fields(garbage_text)
    assert garbage_res.success is True
    # Missing fields should not be fabricated
    assert garbage_res.get_field("mrp") is None
    assert garbage_res.get_field("date_of_manufacture") is None
