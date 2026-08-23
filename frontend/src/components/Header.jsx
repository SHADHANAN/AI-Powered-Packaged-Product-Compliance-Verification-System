import React from "react";
import { ShieldCheck, Scale, Sparkles } from "lucide-react";

export default function Header() {
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

        <div className="header-meta">
          <div className="status-pill">
            <span className="status-indicator-dot"></span>
            <span>LM Rules Engine v1.0</span>
          </div>
        </div>
      </div>
    </header>
  );
}
