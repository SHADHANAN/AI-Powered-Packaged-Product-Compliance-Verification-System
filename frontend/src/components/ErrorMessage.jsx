import React from "react";
import { AlertTriangle, XCircle, RefreshCw } from "lucide-react";

export default function ErrorMessage({ message, onRetry, onDismiss }) {
  if (!message) return null;

  return (
    <div className="error-banner">
      <div className="error-icon-wrapper">
        <AlertTriangle className="w-5 h-5 text-rose-400" />
      </div>
      <div className="flex-1">
        <h4 className="error-title">Verification Issue</h4>
        <p className="error-text">{message}</p>
      </div>
      <div className="error-actions">
        {onRetry && (
          <button onClick={onRetry} className="btn-secondary-sm">
            <RefreshCw className="w-3.5 h-3.5 mr-1" /> Retry
          </button>
        )}
        {onDismiss && (
          <button onClick={onDismiss} className="btn-icon-sm" title="Dismiss">
            <XCircle className="w-4 h-4 text-slate-400 hover:text-slate-200" />
          </button>
        )}
      </div>
    </div>
  );
}
