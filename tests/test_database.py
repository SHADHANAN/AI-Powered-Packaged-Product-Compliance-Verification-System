from sqlalchemy.orm import Session
from backend.config import get_settings
from backend.database.models import Product, Verification, ExtractedField, ComplianceCheck
from backend.database.connection import Base, create_db_engine


def test_database_configuration():
    """Verify database configuration loads properly."""
    settings = get_settings()
    assert settings.DATABASE_URL is not None
    assert "compliance_db" in settings.DATABASE_URL or "postgresql" in settings.DATABASE_URL


def test_models_import_and_metadata():
    """Verify all models are registered in Base metadata."""
    table_names = list(Base.metadata.tables.keys())
    assert "products" in table_names
    assert "verifications" in table_names
    assert "extracted_fields" in table_names
    assert "compliance_checks" in table_names


def test_product_crud_in_db(db_session: Session):
    """Verify direct Product CRUD operations."""
    product = Product(
        product_name="Organic Green Tea",
        brand_name="TeaCo",
        manufacturer_name="TeaCo India Pvt Ltd, Bangalore",
        importer_name=None,
        country_of_origin="India",
        net_quantity="100",
        unit="g",
        batch_number="TC-2024-001",
        date_of_manufacture="01/2025",
        mrp=250.0,
        customer_care_details="customercare@teaco.in, 1800-123-456",
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    assert product.id is not None
    assert product.product_name == "Organic Green Tea"
    assert product.created_at is not None
    assert product.updated_at is not None

    # Retrieve
    fetched = db_session.get(Product, product.id)
    assert fetched is not None
    assert fetched.brand_name == "TeaCo"


def test_verification_and_relationships(db_session: Session):
    """Verify Verification entity and its relationships with Product, ExtractedField, and ComplianceCheck."""
    product = Product(
        product_name="Almond Milk",
        brand_name="NutriPure",
        country_of_origin="India",
        net_quantity="1",
        unit="L",
        mrp=180.0,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # Create verification
    verification = Verification(
        product_id=product.id,
        verification_status="compliant",
        overall_score=95.5,
        source_image_path="/images/sample_label_01.jpg",
    )
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)

    # Add ExtractedField
    ext_field = ExtractedField(
        verification_id=verification.id,
        field_name="net_quantity",
        field_value="1 L",
        confidence=0.98,
        source_text="NET QTY: 1 L",
    )
    db_session.add(ext_field)

    # Add ComplianceCheck
    check = ComplianceCheck(
        verification_id=verification.id,
        rule_code="LM-R001",
        rule_name="Mandatory Net Quantity Declaration",
        status="pass",
        expected_value="Standard unit (L or ml)",
        actual_value="1 L",
        explanation="Net quantity declaration is compliant with Legal Metrology rules.",
        severity="high",
    )
    db_session.add(check)
    db_session.commit()

    db_session.refresh(verification)

    # Test relationships
    assert verification.product.product_name == "Almond Milk"
    assert len(verification.extracted_fields) == 1
    assert verification.extracted_fields[0].field_name == "net_quantity"
    assert len(verification.compliance_checks) == 1
    assert verification.compliance_checks[0].rule_code == "LM-R001"
    assert len(product.verifications) == 1


def test_cascade_delete(db_session: Session):
    """Verify cascading deletion from product to verifications, extracted fields, and compliance checks."""
    product = Product(product_name="Test Snack")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    verification = Verification(product_id=product.id, verification_status="pending")
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)

    ext = ExtractedField(verification_id=verification.id, field_name="mrp", field_value="50.0")
    check = ComplianceCheck(
        verification_id=verification.id,
        rule_code="LM-R002",
        rule_name="MRP Declaration",
        status="pass",
        severity="critical",
    )
    db_session.add_all([ext, check])
    db_session.commit()

    # Delete product
    db_session.delete(product)
    db_session.commit()

    # Check cascading deletion
    assert db_session.get(Product, product.id) is None
    assert db_session.get(Verification, verification.id) is None
    assert db_session.get(ExtractedField, ext.id) is None
    assert db_session.get(ComplianceCheck, check.id) is None
