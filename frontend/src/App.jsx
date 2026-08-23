import React from "react";
import Header from "./components/Header";
import VerificationPage from "./pages/VerificationPage";
import "./App.css";

export default function App() {
  return (
    <div className="app-layout">
      <Header />
      <div className="app-body">
        <VerificationPage />
      </div>
      <footer className="app-footer">
        <div className="footer-content">
          <p className="text-xs text-slate-500">
            Legal Metrology (Packaged Commodities) Compliance Verification System • Powered by PaddleOCR, Deterministic RuleEngine & Evidence-Grounded AI
          </p>
        </div>
      </footer>
    </div>
  );
}