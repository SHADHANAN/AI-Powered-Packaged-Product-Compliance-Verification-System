import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, RotateCcw, Award, Package, Hash } from "lucide-react";

export default function VerificationSummary({
  overallStatus,
  overallScore,
  verificationId,
  productId,
  onReset,
}) {
  const statusUpper = (overallStatus || "").toUpperCase();

  let statusConfig = {
    badgeClass: "badge-status-compliant",
    borderClass: "card-compliant",
    icon: CheckCircle2,
    label: "COMPLIANT",
    desc: "All evaluated mandatory Legal Metrology declarations are fully satisfied.",
  };

  if (statusUpper === "PARTIALLY_COMPLIANT") {
    statusConfig = {
      badgeClass: "badge-status-partial",
      borderClass: "card-partial",
      icon: AlertTriangle,
      label: "PARTIALLY COMPLIANT",
      desc: "One or more statutory declarations require attention or remediation.",
    };
  } else if (statusUpper === "NON_COMPLIANT" || statusUpper === "ERROR") {
    statusConfig = {
      badgeClass: "badge-status-violation",
      borderClass: "card-violation",
      icon: XCircle,
      label: "NON COMPLIANT",
      desc: "Critical mandatory packaging declarations are missing or invalid.",
    };
  }

  const Icon = statusConfig.icon;

  return (
    <div className={`summary-card ${statusConfig.borderClass}`}>
      <div className="summary-header">
        <div className="flex items-center gap-3">
          <div className={`status-icon-wrapper ${statusConfig.badgeClass}`}>
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`status-badge-lg ${statusConfig.badgeClass}`}>
                {statusConfig.label}
              </span>
              <span className="text-xs text-slate-400">
                Score: <strong className="text-slate-100">{overallScore.toFixed(1)}/100</strong>
              </span>
            </div>
            <p className="summary-desc">{statusConfig.desc}</p>
          </div>
        </div>

        <button onClick={onReset} className="btn-secondary-sm">
          <RotateCcw className="w-3.5 h-3.5 mr-1" /> Verify Another Product
        </button>
      </div>

      <div className="summary-stats-grid">
        <div className="stat-box">
          <Award className="w-4 h-4 text-cyan-400 mb-1" />
          <span className="stat-label">Compliance Score</span>
          <span className="stat-value">{overallScore.toFixed(1)}<span className="text-xs text-slate-400">/100</span></span>
        </div>
        <div className="stat-box">
          <Hash className="w-4 h-4 text-emerald-400 mb-1" />
          <span className="stat-label">Verification ID</span>
          <span className="stat-value">#{verificationId || "--"}</span>
        </div>
        <div className="stat-box">
          <Package className="w-4 h-4 text-indigo-400 mb-1" />
          <span className="stat-label">Product ID</span>
          <span className="stat-value">#{productId || "--"}</span>
        </div>
      </div>
    </div>
  );
}
