import React, { useState } from "react";
import { FileText, ChevronDown, ChevronUp, Copy, Check } from "lucide-react";

export default function OCRResults({ ocr }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!ocr || !ocr.text) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(ocr.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="section-card">
      <div
        className="section-header cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <h3 className="section-title">Optical Character Recognition (OCR)</h3>
          <span className="badge-meta">
            Confidence: {(ocr.average_confidence * 100).toFixed(1)}%
          </span>
          <span className="badge-meta">
            {ocr.line_count || ocr.text.split("\n").length} Lines
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      {isOpen && (
        <div className="section-body">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-slate-400">Raw Recognized Label Text:</span>
            <button
              onClick={handleCopy}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copied ? "Copied" : "Copy text"}
            </button>
          </div>
          <pre className="ocr-text-box">{ocr.text}</pre>
        </div>
      )}
    </div>
  );
}
