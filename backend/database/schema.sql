-- AI-Powered Packaged Product Compliance Verification System
-- PostgreSQL Database Schema

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255),
    manufacturer_name VARCHAR(255),
    importer_name VARCHAR(255),
    country_of_origin VARCHAR(100),
    net_quantity VARCHAR(100),
    unit VARCHAR(50),
    batch_number VARCHAR(100),
    date_of_manufacture VARCHAR(100),
    date_of_import VARCHAR(100),
    mrp DOUBLE PRECISION,
    customer_care_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_product_name ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_products_brand_name ON products(brand_name);

-- 2. Verifications Table
CREATE TABLE IF NOT EXISTS verifications (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    verification_status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    overall_score DOUBLE PRECISION,
    source_image_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_verifications_product_id ON verifications(product_id);
CREATE INDEX IF NOT EXISTS idx_verifications_status ON verifications(verification_status);

-- 3. Extracted Fields Table
CREATE TABLE IF NOT EXISTS extracted_fields (
    id SERIAL PRIMARY KEY,
    verification_id INTEGER NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT,
    confidence DOUBLE PRECISION,
    source_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_extracted_fields_verification_id ON extracted_fields(verification_id);
CREATE INDEX IF NOT EXISTS idx_extracted_fields_field_name ON extracted_fields(field_name);

-- 4. Compliance Checks Table
CREATE TABLE IF NOT EXISTS compliance_checks (
    id SERIAL PRIMARY KEY,
    verification_id INTEGER NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
    rule_code VARCHAR(100) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    expected_value TEXT,
    actual_value TEXT,
    explanation TEXT,
    severity VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_compliance_checks_verification_id ON compliance_checks(verification_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_rule_code ON compliance_checks(rule_code);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_status ON compliance_checks(status);
