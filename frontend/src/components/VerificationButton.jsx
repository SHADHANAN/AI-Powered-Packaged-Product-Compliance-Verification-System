import React from "react";
import { ShieldCheck, Loader2 } from "lucide-react";

export default function VerificationButton({ onVerify, disabled, loading }) {
  return (
    <div className="verify-action-container">
      <button
        type="button"
        onClick={onVerify}
        disabled={disabled || loading}
        className={`btn-primary-verify ${disabled ? "btn-disabled" : ""}`}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin mr-2" />
            <span>Verifying Compliance...</span>
          </>
        ) : (
          <>
            <ShieldCheck className="w-5 h-5 mr-2" />
            <span>Verify Legal Metrology Compliance</span>
          </>
        )}
      </button>
    </div>
  );
}
