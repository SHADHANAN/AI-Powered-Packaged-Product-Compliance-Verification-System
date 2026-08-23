import React, { useState } from "react";
import Header from "./components/Header";
import VerificationPage from "./pages/VerificationPage";
import VerificationHistory from "./components/VerificationHistory";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("verify");
  const [activeVerificationId, setActiveVerificationId] = useState(null);

  const handleSelectHistoryItem = (id) => {
    setActiveVerificationId(id);
    setActiveTab("verify");
  };

  const handleClearActiveVerification = () => {
    setActiveVerificationId(null);
  };

  return (
    <div className="app-layout">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="app-body">
        {activeTab === "verify" ? (
          <VerificationPage
            activeVerificationId={activeVerificationId}
            onClearActiveVerification={handleClearActiveVerification}
          />
        ) : (
          <VerificationHistory onSelectVerification={handleSelectHistoryItem} />
        )}
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