import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, MinusCircle, Info } from "lucide-react";

export default function ComplianceCheckCard({ check }) {
  const statusUpper = (check.status || "").toUpperCase();
  const severityUpper = (check.severity || "MEDIUM").toUpperCase();

  let statusConfig = {
    badgeClass: "badge-pass",
    icon: CheckCircle2,
    label: "PASS",
  };

  if (statusUpper === "FAIL") {
    statusConfig = {
      badgeClass: "badge-fail",
      icon: XCircle,
      label: "FAIL",
    };
  } else if (statusUpper === "WARN" || statusUpper === "WARNING") {
    statusConfig = {
      badgeClass: "badge-warn",
      icon: AlertTriangle,
      label: "WARN",
    };
  } else if (statusUpper === "NOT_APPLICABLE") {
    statusConfig = {
      badgeClass: "badge-na",
      icon: MinusCircle,
      label: "N/A",
    };
  }

  const Icon = statusConfig.icon;

  const severityClass =
    severityUpper === "CRITICAL"
      ? "badge-severity-critical"
      : severityUpper === "HIGH"
      ? "badge-severity-high"
      : severityUpper === "MEDIUM"
      ? "badge-severity-medium"
      : "badge-severity-low";

  return (
    <div className={`check-card check-card-${statusUpper.toLowerCase()}`}>
      <div className="check-card-header">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 check-status-icon" />
          <span className="check-rule-code">{check.rule_code}</span>
          <span className="check-rule-name">{check.rule_name}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`severity-badge ${severityClass}`}>{severityUpper}</span>
          <span className={`status-pill-badge ${statusConfig.badgeClass}`}>{statusConfig.label}</span>
        </div>
      </div>

      <div className="check-card-body">
        <p className="check-explanation">{check.explanation}</p>

        <div className="check-comparison-grid">
          <div className="comparison-box">
            <span className="comparison-label">Expected Requirement</span>
            <span className="comparison-value text-slate-300">
              {check.expected_value || "--"}
            </span>
          </div>
          <div className="comparison-box">
            <span className="comparison-label">Detected Declaration</span>
            <span className={`comparison-value ${statusUpper === "FAIL" ? "text-rose-400 font-semibold" : "text-slate-200"}`}>
              {check.actual_value || <span className="italic text-slate-500">Missing</span>}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
