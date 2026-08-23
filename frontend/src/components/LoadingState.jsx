import React, { useState, useEffect } from "react";
import { CheckCircle2, Circle, Loader2, Sparkles, Scan, FileSearch, ShieldCheck } from "lucide-react";

const STAGES = [
  { id: "image", label: "Validating image integrity & dimensions", icon: Scan },
  { id: "ocr", label: "Reading packaging text via PaddleOCR", icon: FileSearch },
  { id: "nlp", label: "Extracting statutory declarations & normalizing units", icon: Sparkles },
  { id: "rules", label: "Evaluating Legal Metrology Rule Engine", icon: ShieldCheck },
  { id: "ai", label: "Generating evidence-grounded AI explanation", icon: Sparkles },
];

export default function LoadingState() {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 1600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-card">
      <div className="loading-spinner-wrapper">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
      </div>
      <h3 className="loading-title">Analyzing Packaged Commodity</h3>
      <p className="loading-subtitle">
        Running deterministic regulatory compliance verification pipeline...
      </p>

      <div className="stages-timeline">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStage;
          const isCurrent = idx === currentStage;
          const Icon = stage.icon;

          return (
            <div
              key={stage.id}
              className={`stage-item ${isDone ? "stage-done" : isCurrent ? "stage-current" : "stage-pending"}`}
            >
              <div className="stage-icon-circle">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                ) : (
                  <Circle className="w-3.5 h-3.5 text-slate-500" />
                )}
              </div>
              <span className="stage-label">{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
