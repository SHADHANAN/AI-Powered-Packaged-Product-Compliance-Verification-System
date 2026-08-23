# AI-Powered Packaged Product Compliance Verification System

An AI-powered system designed to verify packaged product compliance with Legal Metrology rules and standards.

## Project Structure

- **`frontend/`**: React + Vite UI interface.
- **`backend/`**: Core API server, database handlers, and routing.
- **`services/`**:
  - `ocr_service`: Text recognition and image preprocessing.
  - `extraction_service`: NLP and regex extraction of packaging declarations.
  - `compliance_service`: Rule evaluation engine for Legal Metrology regulations.
  - `explanation_service`: LLM-powered explanations and report recommendations.
- **`datasets/`**: Annotations and sample datasets.
- **`reports/`**: Generated compliance logs and reports.
- **`tests/`**: Automated unit and integration test suite.
- **`scripts/`**: Utility and pipeline execution scripts.
