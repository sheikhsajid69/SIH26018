"use client";

import { useEffect, useState } from "react";
import { fetchAdmin } from "../adminAuth";

interface AdminReportsData {
  generated_at: string;
  validation_outcomes: Record<string, number>;
  review_cases_by_status: Record<string, number>;
  review_cases_by_priority: Record<string, number>;
  documents_by_type: Record<string, number>;
  total_mutation_events: number;
}

export default function AdminReportsPage() {
  const [reports, setReports] = useState<AdminReportsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAdmin("/api/v1/admin/reports");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setReports(json);
    } catch (err: any) {
      setError(err?.message || "Failed to load statistical reports.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const totalValidations = reports
    ? Object.values(reports.validation_outcomes).reduce((a, b) => a + b, 0)
    : 0;

  const totalCases = reports
    ? Object.values(reports.review_cases_by_status).reduce((a, b) => a + b, 0)
    : 0;

  const totalDocs = reports
    ? Object.values(reports.documents_by_type).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1c2d38] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Statistical Reports & Intelligence</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#00684a] text-[#c3f0d2] font-mono font-semibold">
              ANALYTICS & METRICS
            </span>
          </div>
          <p className="text-sm text-[#7c8c9a] mt-1">
            Aggregated system intelligence, AI validation consistency rates, adjudication pipeline health, and document intake.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 rounded-xl bg-[#00283b] border border-[#1c2d38] text-xs font-semibold text-[#c1ccd6] hover:text-white hover:border-[#00ed64]/40 transition-colors flex items-center gap-2"
          >
            <span>🖨️</span>
            <span>Print Report</span>
          </button>
          <button
            onClick={loadReports}
            className="px-4 py-2 rounded-xl bg-[#1c2d38] text-xs font-mono text-[#c1ccd6] hover:text-white hover:bg-[#253947] transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Validation Runs</span>
          <div className="text-2xl font-bold text-white mt-1">
            {loading ? "..." : totalValidations}
          </div>
          <p className="text-[11px] text-[#00ed64] mt-1">Multi-source cross-checks</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Total Adjudications</span>
          <div className="text-2xl font-bold text-white mt-1">
            {loading ? "..." : totalCases}
          </div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Review pipeline cases</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Documents Ingested</span>
          <div className="text-2xl font-bold text-[#00ed64] mt-1">
            {loading ? "..." : totalDocs}
          </div>
          <p className="text-[11px] text-[#00ed64] mt-1">WORM vault indexed</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Registered Mutations</span>
          <div className="text-2xl font-bold text-[#f5a623] mt-1">
            {loading ? "..." : reports?.total_mutation_events ?? 0}
          </div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Immutable history events</p>
        </div>
      </div>

      {/* Analytical Grids */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card 1: Validation Outcomes */}
        <div className="p-6 rounded-xl bg-[#00283b] border border-[#1c2d38] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
              <span>🧠</span>
              <span>AI Validation Consistency Rates</span>
            </h3>
            <span className="text-[11px] font-mono text-[#7c8c9a]">
              {totalValidations} total executions
            </span>
          </div>

          <p className="text-xs text-[#7c8c9a]">
            Rule 10 & 13 cross-verification matching uploaded documents against authoritative state records.
          </p>

          <div className="space-y-3 pt-2">
            {reports && Object.keys(reports.validation_outcomes).length > 0 ? (
              Object.entries(reports.validation_outcomes).map(([outcome, count]) => {
                const pct = totalValidations > 0 ? Math.round((count / totalValidations) * 100) : 0;
                const isConsistent = outcome.toUpperCase().includes("CONSISTENT") && !outcome.toUpperCase().includes("DISCREPANCY");
                return (
                  <div key={outcome} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className={isConsistent ? "text-[#00ed64] font-bold" : "text-[#fa6e39] font-bold"}>
                        {outcome}
                      </span>
                      <span className="text-[#c1ccd6]">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-[#001e2b] h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${isConsistent ? "bg-[#00ed64]" : "bg-[#fa6e39]"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-[#7c8c9a] italic py-4 text-center">
                No validation data recorded in current database fixture.
              </p>
            )}
          </div>
        </div>

        {/* Card 2: Adjudication Pipeline Status */}
        <div className="p-6 rounded-xl bg-[#00283b] border border-[#1c2d38] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
              <span>⚖️</span>
              <span>Review Case Pipeline Breakdown</span>
            </h3>
            <span className="text-[11px] font-mono text-[#7c8c9a]">
              {totalCases} cases recorded
            </span>
          </div>

          <p className="text-xs text-[#7c8c9a]">
            Status of cases routed to Revenue Officers for adjudication under Rule 11.
          </p>

          <div className="space-y-3 pt-2">
            {reports && Object.keys(reports.review_cases_by_status).length > 0 ? (
              Object.entries(reports.review_cases_by_status).map(([status, count]) => {
                const pct = totalCases > 0 ? Math.round((count / totalCases) * 100) : 0;
                const isResolved = status === "RESOLVED";
                const isReview = status === "IN_REVIEW";
                return (
                  <div key={status} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span
                        className={
                          isResolved
                            ? "text-[#00ed64] font-bold"
                            : isReview
                            ? "text-[#c3f0d2] font-bold"
                            : "text-[#f5a623] font-bold"
                        }
                      >
                        {status}
                      </span>
                      <span className="text-[#c1ccd6]">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-[#001e2b] h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          isResolved ? "bg-[#00ed64]" : isReview ? "bg-[#00684a]" : "bg-[#f5a623]"
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-[#7c8c9a] italic py-4 text-center">
                No review cases currently in database.
              </p>
            )}
          </div>
        </div>

        {/* Card 3: Priority Distribution */}
        <div className="p-6 rounded-xl bg-[#00283b] border border-[#1c2d38] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
              <span>🎯</span>
              <span>Case Priority Distribution</span>
            </h3>
            <span className="text-[11px] font-mono text-[#7c8c9a]">Urgency Tiers</span>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-[#001e2b] border border-[#fa6e39]/30 text-center">
              <span className="text-[10px] uppercase font-mono text-[#fa6e39] font-bold block">
                P1 HIGH
              </span>
              <div className="text-xl font-bold text-white mt-1">
                {reports?.review_cases_by_priority["P1_HIGH"] ?? 0}
              </div>
              <span className="text-[10px] text-[#7c8c9a]">Critical Discrepancy</span>
            </div>

            <div className="p-3 rounded-xl bg-[#001e2b] border border-[#f5a623]/30 text-center">
              <span className="text-[10px] uppercase font-mono text-[#f5a623] font-bold block">
                P2 NORMAL
              </span>
              <div className="text-xl font-bold text-white mt-1">
                {reports?.review_cases_by_priority["P2_NORMAL"] ?? 0}
              </div>
              <span className="text-[10px] text-[#7c8c9a]">Standard Review</span>
            </div>

            <div className="p-3 rounded-xl bg-[#001e2b] border border-[#00ed64]/30 text-center">
              <span className="text-[10px] uppercase font-mono text-[#00ed64] font-bold block">
                P3 ADVISORY
              </span>
              <div className="text-xl font-bold text-white mt-1">
                {reports?.review_cases_by_priority["P3_ADVISORY"] ?? 0}
              </div>
              <span className="text-[10px] text-[#7c8c9a]">Informational</span>
            </div>
          </div>
        </div>

        {/* Card 4: Document Intake by Type */}
        <div className="p-6 rounded-xl bg-[#00283b] border border-[#1c2d38] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
              <span>📂</span>
              <span>Document Intake Classification</span>
            </h3>
            <span className="text-[11px] font-mono text-[#7c8c9a]">
              {totalDocs} files
            </span>
          </div>

          <div className="space-y-2 pt-2">
            {reports && Object.keys(reports.documents_by_type).length > 0 ? (
              Object.entries(reports.documents_by_type).map(([type, count]) => (
                <div
                  key={type}
                  className="flex items-center justify-between p-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-xs font-mono"
                >
                  <span className="text-white">{type}</span>
                  <span className="px-2 py-0.5 rounded bg-[#00684a]/30 text-[#00ed64] font-bold">
                    {count}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-[#7c8c9a] italic py-4 text-center">
                No documents indexed in vault.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Institutional Advisory Disclaimer */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38] text-xs text-[#7c8c9a] font-mono leading-relaxed">
        <strong className="text-white">SIH26018 Institutional Notice:</strong> All metrics, validation percentages, and review stats presented herein reflect synthetic sandbox operations. LANDSYNC AI serves as an advisory decision-support system and does not claim statutory land registry certification authority.
      </div>
    </div>
  );
}
