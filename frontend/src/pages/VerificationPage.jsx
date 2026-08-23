import React, { useState, useEffect } from "react";
import ImageUploader from "../components/ImageUploader";
import VerificationButton from "../components/VerificationButton";
import LoadingState from "../components/LoadingState";
import ErrorMessage from "../components/ErrorMessage";
import VerificationSummary from "../components/VerificationSummary";
import ExtractedFields from "../components/ExtractedFields";
import ComplianceResults from "../components/ComplianceResults";
import AIExplanation from "../components/AIExplanation";
import Recommendations from "../components/Recommendations";
import OCRResults from "../components/OCRResults";
import { verifyProductImage, getVerificationById } from "../services/api";

export default function VerificationPage({ activeVerificationId, onClearActiveVerification }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [strategy, setStrategy] = useState("standard");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [result, setResult] = useState(null);

  // If an activeVerificationId is passed from History, load details
  useEffect(() => {
    if (activeVerificationId) {
      loadVerificationDetails(activeVerificationId);
    }
  }, [activeVerificationId]);

  const loadVerificationDetails = async (id) => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await getVerificationById(id);
      if (data) {
        // Map database model fields to result schema
        const mappedResult = {
          success: true,
          verification_id: data.id,
          product_id: data.product_id,
          overall_status: data.verification_status,
          overall_score: data.overall_score || 100.0,
          extracted_fields: data.extracted_fields || [],
          compliance_checks: data.compliance_checks || [],
          ocr: {
            text: data.extracted_fields?.map((f) => f.source_text).filter(Boolean).join("\n") || "Historical text logged in session.",
            average_confidence: 0.95,
            line_count: data.extracted_fields?.length || 0,
          },
          explanation: {
            summary: `Inspection session #${data.id} recorded on ${new Date(data.completed_at || data.created_at).toLocaleDateString()}. Overall compliance status: ${data.verification_status.toUpperCase()}.`,
            items: data.compliance_checks?.map((c) => ({
              rule_code: c.rule_code,
              rule_name: c.rule_name,
              status: c.status,
              severity: c.severity,
              explanation: c.explanation,
              why_it_matters: "Statutory mandatory declaration mandated under Legal Metrology Rules.",
              recommended_action: c.status === "PASS" ? "Declaration is compliant." : `Remediate: ${c.expected_value}`,
              evidence: `Actual: ${c.actual_value || 'Missing'}`,
              confidence: 0.95,
            })) || [],
            recommendations: data.compliance_checks?.filter((c) => (c.status || '').toUpperCase() === 'FAIL').map((c) => `Remediate ${c.rule_name} (${c.rule_code}): Provide ${c.expected_value}`) || ["All statutory packaging declarations meet verified standards."],
            ai_generated: false,
          },
        };
        setResult(mappedResult);
      }
    } catch (err) {
      console.error("Failed to load historical verification:", err);
      setErrorMessage("Failed to load verification session details.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setErrorMessage(null);
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setErrorMessage(null);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setErrorMessage(null);
    setLoading(false);
    if (onClearActiveVerification) onClearActiveVerification();
  };

  const handleVerify = async () => {
    if (!selectedFile) {
      setErrorMessage("Please select a packaged product image before starting verification.");
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setResult(null);

    try {
      const data = await verifyProductImage(selectedFile, strategy);
      if (data && data.success) {
        setResult(data);
      } else {
        setErrorMessage(
          data?.error_message || "Verification failed to complete. Please try another image."
        );
      }
    } catch (err) {
      console.error("Verification error:", err);
      const detailMsg =
        err.response?.data?.error?.message ||
        err.response?.data?.detail ||
        err.message ||
        "Unable to connect to the verification service. Ensure backend server is running.";
      setErrorMessage(detailMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main-content-layout">
      {/* Upload Panel */}
      {!result && (
        <div className="upload-container-wrapper">
          <div className="text-center mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-100">
              Packaged Product Compliance Verification
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl mx-auto">
              Automated statutory compliance audit against Indian Legal Metrology (Packaged Commodities) Rules, 2011.
            </p>
          </div>

          <ImageUploader
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            onFileRemove={handleFileRemove}
            onFileError={(err) => setErrorMessage(err)}
            strategy={strategy}
            onStrategyChange={setStrategy}
            disabled={loading}
          />

          {errorMessage && (
            <div className="mt-4">
              <ErrorMessage
                message={errorMessage}
                onRetry={selectedFile ? handleVerify : null}
                onDismiss={() => setErrorMessage(null)}
              />
            </div>
          )}

          {!loading && (
            <VerificationButton
              onVerify={handleVerify}
              disabled={!selectedFile}
              loading={loading}
            />
          )}

          {loading && (
            <div className="mt-6">
              <LoadingState />
            </div>
          )}
        </div>
      )}

      {/* Verification Results View */}
      {result && (
        <div className="results-container space-y-6">
          <VerificationSummary
            overallStatus={result.overall_status}
            overallScore={result.overall_score}
            verificationId={result.verification_id}
            productId={result.product_id}
            onReset={handleReset}
          />

          {/* AI Explanation & Remediation */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AIExplanation explanation={result.explanation} />
            </div>
            <div>
              <Recommendations
                recommendations={result.explanation?.recommendations || []}
              />
            </div>
          </div>

          {/* Compliance Checks List */}
          <ComplianceResults checks={result.compliance_checks || []} />

          {/* Extracted Product Fields */}
          <ExtractedFields extractedFields={result.extracted_fields || []} />

          {/* Collapsible Raw OCR Results */}
          <OCRResults ocr={result.ocr} />
        </div>
      )}
    </main>
  );
}
