"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAdmin } from "../adminAuth";

interface ReviewCaseItem {
  id: string;
  parcel_id: string;
  reason: string;
  severity: string;
  status: string;
  priority: string;
  discrepancy_field?: string;
  claimed_value?: string;
  authoritative_value?: string;
  assigned_officer?: string;
  reviewer_notes?: string;
  resolution?: string;
  created_at?: string;
  resolved_at?: string;
}

export default function AdminReviewCasesPage() {
  const [cases, setCases] = useState<ReviewCaseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [search, setSearch] = useState("");

  // Inspector modal
  const [selectedCase, setSelectedCase] = useState<ReviewCaseItem | null>(null);

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      if (priorityFilter) params.append("priority", priorityFilter);
      if (search) params.append("search", search);

      const res = await fetchAdmin(`/api/v1/admin/review-cases?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setCases(json.cases || []);
      setTotal(json.total || 0);
    } catch (err: any) {
      setError(err?.message || "Failed to load review cases.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [statusFilter, priorityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadCases();
  };

  // Aggregates
  const openCount = cases.filter((c) => c.status === "OPEN").length;
  const p1Count = cases.filter((c) => c.priority === "P1_HIGH").length;
  const resolvedCount = cases.filter((c) => c.status === "RESOLVED").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1c2d38] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Review Case Oversight</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#00684a] text-[#c3f0d2] font-mono font-semibold">
              ADJUDICATION PIPELINE
            </span>
          </div>
          <p className="text-sm text-[#7c8c9a] mt-1">
            System-wide registry of AI-flagged land inconsistencies, boundary disputes, and officer determinations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadCases}
            className="px-4 py-2 rounded-xl bg-[#1c2d38] text-xs font-mono text-[#c1ccd6] hover:text-white hover:bg-[#253947] transition-colors"
          >
            🔄 Refresh Cases
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Total Indexed Cases</span>
          <div className="text-2xl font-bold text-white mt-1">{total}</div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Across all cadastral divisions</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Open / Pending</span>
          <div className="text-2xl font-bold text-[#f5a623] mt-1">{openCount}</div>
          <p className="text-[11px] text-[#f5a623] mt-1 flex items-center gap-1">
            <span>⏳</span> Requiring officer action
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">High Priority (P1)</span>
          <div className="text-2xl font-bold text-[#fa6e39] mt-1">{p1Count}</div>
          <p className="text-[11px] text-[#fa6e39] mt-1 flex items-center gap-1">
            <span>⚠️</span> Critical discrepancy
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Resolved Decisions</span>
          <div className="text-2xl font-bold text-[#00ed64] mt-1">{resolvedCount}</div>
          <p className="text-[11px] text-[#00ed64] mt-1 flex items-center gap-1">
            <span>✓</span> Adjudicated & logged
          </p>
        </div>
      </div>

      {/* Institutional Boundary Callout */}
      <div className="p-4 rounded-xl bg-[#00283b]/70 border border-[#1c2d38] text-xs text-[#c1ccd6] flex items-start gap-3">
        <span className="text-base">🛡️</span>
        <div>
          <span className="text-white font-semibold">Governance Principle — Human-in-the-Loop Adjudication:</span>{" "}
          AI anomaly detection flags potential boundary or name discrepancies strictly in an <em className="text-[#00ed64]">advisory capacity</em>.
          Official resolutions, parcel boundary corrections, or rejection of claims require explicit officer sign-off with permanent audit trails.
        </div>
      </div>

      {/* Filters & Search */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38] flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <input
            type="text"
            placeholder="Search by Parcel ID (e.g. KA-BLR-) or discrepancy reason..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white placeholder-[#5c6c7a] focus:outline-none focus:border-[#00ed64]"
          />
          <span className="absolute left-3 top-2.5 text-xs text-[#5c6c7a]">🔍</span>
        </form>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white focus:outline-none focus:border-[#00ed64]"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="IN_REVIEW">IN_REVIEW</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white focus:outline-none focus:border-[#00ed64]"
          >
            <option value="">All Priorities</option>
            <option value="P1_HIGH">P1 HIGH</option>
            <option value="P2_NORMAL">P2 NORMAL</option>
            <option value="P3_ADVISORY">P3 ADVISORY</option>
          </select>

          {(statusFilter || priorityFilter || search) && (
            <button
              onClick={() => {
                setStatusFilter("");
                setPriorityFilter("");
                setSearch("");
              }}
              className="px-3 py-2 text-xs text-[#7c8c9a] hover:text-white"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 rounded-xl bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-xs text-[#fa6e39] flex items-center justify-between">
          <span>{error}</span>
          <button onClick={loadCases} className="font-bold underline ml-2">
            Retry
          </button>
        </div>
      )}

      {/* Table */}
      <div className="rounded-xl bg-[#00283b] border border-[#1c2d38] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#001e2b] border-b border-[#1c2d38] text-[#7c8c9a] font-mono uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-5 py-3">Case ID</th>
                <th className="px-5 py-3">Parcel Reference</th>
                <th className="px-5 py-3">Discrepancy Reason</th>
                <th className="px-5 py-3">Priority</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Assigned Officer</th>
                <th className="px-5 py-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c2d38]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a] font-mono">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
                      <span>Loading review cases...</span>
                    </div>
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a]">
                    No review cases found matching criteria.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id} className="hover:bg-[#002233] transition-colors">
                    {/* Case ID */}
                    <td className="px-5 py-4 font-mono font-bold text-white">
                      {c.id}
                      <span className="block text-[10px] text-[#7c8c9a] font-normal">
                        {c.created_at ? new Date(c.created_at).toLocaleDateString() : "—"}
                      </span>
                    </td>

                    {/* Parcel ID */}
                    <td className="px-5 py-4">
                      <span className="px-2.5 py-1 rounded bg-[#001e2b] border border-[#1c2d38] font-mono text-[11px] text-[#00ed64]">
                        {c.parcel_id}
                      </span>
                    </td>

                    {/* Reason */}
                    <td className="px-5 py-4 max-w-xs truncate text-[#c1ccd6]">
                      <span title={c.reason}>{c.reason}</span>
                      {c.discrepancy_field && (
                        <span className="block text-[10px] font-mono text-[#7c8c9a]">
                          Field: {c.discrepancy_field}
                        </span>
                      )}
                    </td>

                    {/* Priority */}
                    <td className="px-5 py-4 font-mono text-[10px]">
                      <span
                        className={`px-2 py-0.5 rounded font-bold ${
                          c.priority === "P1_HIGH"
                            ? "bg-[#fa6e39]/10 text-[#fa6e39] border border-[#fa6e39]/20"
                            : c.priority === "P2_NORMAL"
                            ? "bg-[#f5a623]/10 text-[#f5a623] border border-[#f5a623]/20"
                            : "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                        }`}
                      >
                        {c.priority}
                      </span>
                    </td>

                    {/* Status */}
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                          c.status === "RESOLVED"
                            ? "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                            : c.status === "IN_REVIEW"
                            ? "bg-[#00684a]/20 text-[#c3f0d2] border border-[#00684a]"
                            : "bg-[#f5a623]/10 text-[#f5a623] border border-[#f5a623]/20"
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            c.status === "RESOLVED"
                              ? "bg-[#00ed64]"
                              : c.status === "IN_REVIEW"
                              ? "bg-[#00ed64]"
                              : "bg-[#f5a623]"
                          }`}
                        />
                        {c.status}
                      </span>
                    </td>

                    {/* Assigned Officer */}
                    <td className="px-5 py-4 font-mono text-xs text-[#c1ccd6]">
                      {c.assigned_officer ? `@${c.assigned_officer}` : <span className="text-[#5c6c7a]">Unassigned</span>}
                    </td>

                    {/* Inspect Button */}
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={() => setSelectedCase(c)}
                        className="px-3 py-1.5 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-xs font-semibold text-[#00ed64] hover:bg-[#00684a]/20 transition-colors"
                      >
                        Inspect →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Case Inspector Modal */}
      {selectedCase && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#1c2d38] pb-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#00ed64]">Advisory Case Details</span>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>{selectedCase.id}</span>
                  <span className="text-xs px-2 py-0.5 rounded font-mono bg-[#001e2b] border border-[#1c2d38] text-[#c1ccd6]">
                    {selectedCase.parcel_id}
                  </span>
                </h3>
              </div>
              <button
                onClick={() => setSelectedCase(null)}
                className="w-8 h-8 rounded-full bg-[#1c2d38] text-[#7c8c9a] hover:text-white flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-2">
                <span className="text-[10px] uppercase font-mono text-[#7c8c9a] block">Discrepancy Summary</span>
                <p className="text-sm font-semibold text-white">{selectedCase.reason}</p>
                <div className="grid grid-cols-2 gap-3 pt-2 text-[11px] font-mono border-t border-[#1c2d38]">
                  <div>
                    <span className="text-[#7c8c9a] block">Discrepancy Field:</span>
                    <span className="text-[#00ed64]">{selectedCase.discrepancy_field || "Not specified"}</span>
                  </div>
                  <div>
                    <span className="text-[#7c8c9a] block">Severity / Priority:</span>
                    <span className="text-white">{selectedCase.severity} / {selectedCase.priority}</span>
                  </div>
                </div>
              </div>

              {/* Value Comparison */}
              {(selectedCase.claimed_value || selectedCase.authoritative_value) && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38]">
                    <span className="text-[10px] font-mono text-[#fa6e39] uppercase block mb-1">
                      📄 Document Claimed Value
                    </span>
                    <p className="font-mono text-sm text-white font-bold">
                      {selectedCase.claimed_value || "N/A"}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38]">
                    <span className="text-[10px] font-mono text-[#00ed64] uppercase block mb-1">
                      🏛️ Authority Record Value
                    </span>
                    <p className="font-mono text-sm text-white font-bold">
                      {selectedCase.authoritative_value || "N/A"}
                    </p>
                  </div>
                </div>
              )}

              {/* Status and Officer Notes */}
              <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-2">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span>Assigned Officer: <strong className="text-white">@{selectedCase.assigned_officer || "None"}</strong></span>
                  <span>Status: <strong className="text-[#00ed64]">{selectedCase.status}</strong></span>
                </div>
                {selectedCase.reviewer_notes && (
                  <div className="pt-2 border-t border-[#1c2d38]">
                    <span className="text-[10px] font-mono text-[#7c8c9a] uppercase block mb-1">Officer Notes</span>
                    <p className="text-white text-xs">{selectedCase.reviewer_notes}</p>
                  </div>
                )}
                {selectedCase.resolution && (
                  <div className="pt-2 border-t border-[#1c2d38]">
                    <span className="text-[10px] font-mono text-[#7c8c9a] uppercase block mb-1">Recorded Determination</span>
                    <p className="text-[#00ed64] font-semibold text-xs">{selectedCase.resolution}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-[#1c2d38]">
              <span className="text-[10px] font-mono text-[#5c6c7a]">
                Adjudications are strictly recorded in accordance with Rule 11.
              </span>
              <button
                onClick={() => setSelectedCase(null)}
                className="px-5 py-2 rounded-xl bg-[#00684a] text-white hover:bg-[#00ed64] hover:text-[#001e2b] font-bold text-xs transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
