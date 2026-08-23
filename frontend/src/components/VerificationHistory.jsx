import React, { useState, useEffect } from "react";
import { History, Search, RefreshCw, CheckCircle2, AlertTriangle, XCircle, ArrowRight, FileText, Download, Calendar, Package } from "lucide-react";
import { getVerificationHistory, getVerificationReport } from "../services/api";

export default function VerificationHistory({ onSelectVerification }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getVerificationHistory(0, 50);
      setHistoryItems(data.items || []);
    } catch (err) {
      console.error("Failed to fetch verification history:", err);
      setError("Unable to load inspection history from server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDownloadReport = async (e, verificationId, productName) => {
    e.stopPropagation();
    try {
      const report = await getVerificationReport(verificationId);
      if (report && report.markdown_report) {
        const blob = new Blob([report.markdown_report], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Compliance_Report_#${verificationId}_${(productName || "Product").replace(/\s+/g, "_")}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      alert("Failed to download compliance report.");
    }
  };

  const filteredItems = historyItems.filter((item) => {
    const q = searchQuery.toLowerCase();
    const prodName = (item.product?.product_name || "").toLowerCase();
    const brandName = (item.product?.brand_name || "").toLowerCase();
    const status = (item.verification_status || "").toLowerCase();
    const idStr = String(item.id);
    return prodName.includes(q) || brandName.includes(q) || status.includes(q) || idStr.includes(q);
  });

  return (
    <div className="history-container space-y-4">
      <div className="section-card">
        <div className="section-header flex justify-between items-center flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <h3 className="section-title">Inspection History & Audit Logs</h3>
            <span className="badge-meta">{historyItems.length} Records</span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter by product, brand, ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1 text-xs bg-slate-900/80 border border-slate-700 rounded-md text-slate-200 focus:outline-none focus:border-cyan-400 w-56"
              />
            </div>
            <button
              onClick={fetchHistory}
              className="btn-secondary-sm"
              title="Refresh History"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        <div className="p-4">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-cyan-400 mb-2" />
              Loading inspection sessions...
            </div>
          ) : error ? (
            <div className="py-8 text-center text-rose-400 text-sm">{error}</div>
          ) : filteredItems.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              <Package className="w-8 h-8 mx-auto text-slate-600 mb-2" />
              {searchQuery ? "No matching verification records found." : "No verification sessions recorded yet."}
            </div>
          ) : (
            <div className="history-table-wrapper overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-700/60 text-slate-400 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Session ID</th>
                    <th className="py-2.5 px-3">Product Name & Brand</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Score</th>
                    <th className="py-2.5 px-3">Audit Date</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredItems.map((item) => {
                    const statusUpper = (item.verification_status || "COMPLIANT").toUpperCase();
                    const isCompliant = statusUpper === "COMPLIANT";
                    const isPartial = statusUpper === "PARTIALLY_COMPLIANT";

                    const badgeClass = isCompliant
                      ? "badge-status-compliant"
                      : isPartial
                      ? "badge-status-partial"
                      : "badge-status-violation";

                    const StatusIcon = isCompliant
                      ? CheckCircle2
                      : isPartial
                      ? AlertTriangle
                      : XCircle;

                    const dateStr = item.completed_at || item.created_at;
                    const formattedDate = dateStr
                      ? new Date(dateStr).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "--";

                    return (
                      <tr
                        key={item.id}
                        onClick={() => onSelectVerification(item.id)}
                        className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-3 font-mono font-bold text-cyan-400">
                          #{item.id}
                        </td>
                        <td className="py-3 px-3 font-semibold text-slate-200">
                          <div className="flex flex-col">
                            <span>{item.product?.product_name || "Packaged Product"}</span>
                            {item.product?.brand_name && (
                              <span className="text-[10px] text-slate-400 font-normal">
                                Brand: {item.product.brand_name}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded ${badgeClass}`}>
                            <StatusIcon className="w-3 h-3" />
                            {statusUpper}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-bold text-slate-100">
                          {item.overall_score !== null ? `${item.overall_score.toFixed(1)}/100` : "--"}
                        </td>
                        <td className="py-3 px-3 text-slate-400 whitespace-nowrap">
                          {formattedDate}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={(e) => handleDownloadReport(e, item.id, item.product?.product_name)}
                              className="btn-secondary-sm text-[10px] py-1 px-2"
                              title="Download Report (.md)"
                            >
                              <Download className="w-3 h-3 mr-1 text-emerald-400" /> Report
                            </button>
                            <button
                              onClick={() => onSelectVerification(item.id)}
                              className="btn-secondary-sm text-[10px] py-1 px-2"
                              title="View Details"
                            >
                              Details <ArrowRight className="w-3 h-3 ml-1 text-cyan-400" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
