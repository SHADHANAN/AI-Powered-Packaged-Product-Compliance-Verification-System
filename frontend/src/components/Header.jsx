import React from "react";
import { ShieldCheck, Scale, ScanLine, History } from "lucide-react";

export default function Header({ activeTab, onTabChange }) {
  return (
    <header className="header-container">
      <div className="header-content">
        <div className="header-brand">
          <div className="header-logo-badge">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            <Scale className="w-4 h-4 text-cyan-400 absolute -bottom-1 -right-1" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="header-title">MetroCheck AI</h1>
              <span className="badge-regulatory">Legal Metrology</span>
            </div>
            <p className="header-subtitle">
              AI-Powered Packaged Product Compliance Verification System
            </p>
          </div>
        </div>

        <div className="header-actions flex items-center gap-3">
          <div className="nav-tabs flex bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => onTabChange("verify")}
              className={`nav-tab flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-md transition-all ${activeTab === "verify" ? "bg-cyan-600 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"}`}
            >
              <ScanLine className="w-3.5 h-3.5" />
              <span>Verify Product</span>
            </button>
            <button
              onClick={() => onTabChange("history")}
              className={`nav-tab flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-md transition-all ${activeTab === "history" ? "bg-cyan-600 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"}`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Inspection History</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
