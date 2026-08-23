import React, { useState } from "react";
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
import { verifyProductImage } from "../services/api";

export default function VerificationPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [strategy, setStrategy] = useState("standard");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [result, setResult] = useState(null);

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
      {/* Upload Panel (Always visible before result, or can be collapsed when result is present) */}
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
