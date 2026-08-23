import React from "react";
import { CheckCircle2, AlertCircle, ArrowRight, Lightbulb } from "lucide-react";

export default function Recommendations({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="section-card">
        <div className="section-header">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <h3 className="section-title">Packaging Remediation Recommendations</h3>
          </div>
        </div>
        <div className="p-4 text-sm text-slate-400">
          No remediation actions required. Package satisfies statutory standards.
        </div>
      </div>
    );
  }

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <h3 className="section-title">Actionable Packaging Remediation</h3>
          <span className="badge-meta">{recommendations.length} Actions Required</span>
        </div>
      </div>

      <div className="p-4 space-y-2.5">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="recommendation-item">
            <div className="rec-bullet-icon">
              <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-medium">
              {rec}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
