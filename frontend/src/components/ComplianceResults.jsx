import React, { useState } from "react";
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import ComplianceCheckCard from "./ComplianceCheckCard";

export default function ComplianceResults({ checks }) {
  const [filter, setFilter] = useState("ALL");

  if (!checks || checks.length === 0) return null;

  const passedCount = checks.filter((c) => (c.status || "").toUpperCase() === "PASS").length;
  const failedCount = checks.filter((c) => (c.status || "").toUpperCase() === "FAIL").length;
  const warnCount = checks.filter((c) => ["WARN", "WARNING"].includes((c.status || "").toUpperCase())).length;

  const filteredChecks = checks.filter((c) => {
    const s = (c.status || "").toUpperCase();
    if (filter === "FAIL") return s === "FAIL";
    if (filter === "PASS") return s === "PASS";
    if (filter === "WARN") return ["WARN", "WARNING"].includes(s);
    return true;
  });

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <h3 className="section-title">Legal Metrology Compliance Checks</h3>
          <span className="badge-meta">{checks.length} Rules Evaluated</span>
        </div>

        <div className="filter-tabs">
          <button
            onClick={() => setFilter("ALL")}
            className={`filter-tab ${filter === "ALL" ? "filter-tab-active" : ""}`}
          >
            All ({checks.length})
          </button>
          <button
            onClick={() => setFilter("FAIL")}
            className={`filter-tab ${filter === "FAIL" ? "filter-tab-active text-rose-400" : ""}`}
          >
            Failed ({failedCount})
          </button>
          <button
            onClick={() => setFilter("WARN")}
            className={`filter-tab ${filter === "WARN" ? "filter-tab-active text-amber-400" : ""}`}
          >
            Warnings ({warnCount})
          </button>
          <button
            onClick={() => setFilter("PASS")}
            className={`filter-tab ${filter === "PASS" ? "filter-tab-active text-emerald-400" : ""}`}
          >
            Passed ({passedCount})
          </button>
        </div>
      </div>

      <div className="checks-list">
        {filteredChecks.map((chk, idx) => (
          <ComplianceCheckCard key={chk.rule_code || idx} check={chk} />
        ))}
      </div>
    </div>
  );
}
