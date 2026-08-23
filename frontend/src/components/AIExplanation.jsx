import React from "react";
import { Sparkles, Bot, Shield, CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";

export default function AIExplanation({ explanation }) {
  if (!explanation) return null;

  const isAIGenerated = explanation.ai_generated;
  const items = explanation.items || [];

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <h3 className="section-title">Evidence-Grounded Legal Explanation</h3>
        </div>

        <div className="flex items-center gap-2">
          {isAIGenerated ? (
            <span className="badge-ai-mode">
              <Bot className="w-3 h-3 mr-1" /> AI Generated
            </span>
          ) : (
            <span className="badge-fallback-mode">
              <Shield className="w-3 h-3 mr-1" /> Rule Engine Baseline
            </span>
          )}
        </div>
      </div>

      <div className="explanation-body">
        {/* Executive Summary */}
        <div className="explanation-summary-box">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-purple-300 mb-1">
            Executive Summary
          </h4>
          <p className="text-sm text-slate-200 leading-relaxed">
            {explanation.summary}
          </p>
        </div>

        {/* Detailed Item Explanations */}
        {items.length > 0 && (
          <div className="explanation-items-list">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 mt-4">
              Rule-by-Rule Legal Rationale & Remediation
            </h4>
            <div className="space-y-3">
              {items.map((item, idx) => {
                const isFail = item.status === "FAIL";
                const isWarn = ["WARN", "WARNING"].includes(item.status);

                return (
                  <div
                    key={item.rule_code || idx}
                    className={`explanation-item-card ${isFail ? "border-l-rose-500" : isWarn ? "border-l-amber-500" : "border-l-emerald-500"}`}
                  >
                    <div className="flex justify-between items-start mb-1.5">
                      <div className="font-semibold text-sm text-slate-100 flex items-center gap-1.5">
                        <span className="text-xs text-cyan-400 font-mono">{item.rule_code}</span>
                        <span>{item.rule_name}</span>
                      </div>
                      <span className="text-[11px] text-slate-400">
                        {Math.round((item.confidence || 0.95) * 100)}% conf
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mb-2">{item.explanation}</p>

                    <div className="explanation-details-grid">
                      {item.why_it_matters && (
                        <div className="explanation-detail-col">
                          <span className="detail-col-title text-indigo-300">Why It Matters:</span>
                          <span className="detail-col-content text-slate-300">{item.why_it_matters}</span>
                        </div>
                      )}
                      {item.recommended_action && (
                        <div className="explanation-detail-col">
                          <span className="detail-col-title text-emerald-300">Recommended Action:</span>
                          <span className="detail-col-content text-slate-200">{item.recommended_action}</span>
                        </div>
                      )}
                    </div>

                    {item.evidence && (
                      <div className="mt-2 text-[11px] text-slate-400 font-mono bg-slate-900/60 px-2 py-1 rounded">
                        <span className="text-slate-500">Evidence: </span>{item.evidence}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
