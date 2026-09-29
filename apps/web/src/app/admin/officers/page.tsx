"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAdmin } from "../adminAuth";

interface OfficerWorkload {
  assigned_cases: number;
  pending_cases: number;
  resolved_cases: number;
}

interface OfficerItem {
  id: string;
  username: string;
  name: string;
  email: string;
  jurisdiction: string;
  status: string;
  workload: OfficerWorkload;
  last_login?: string;
  created_at?: string;
}

export default function AdminOfficersPage() {
  const [officers, setOfficers] = useState<OfficerItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const loadOfficers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAdmin("/api/v1/admin/officers");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setOfficers(json.officers || []);
      setTotal(json.total || 0);
    } catch (err: any) {
      setError(err?.message || "Failed to load revenue officer roster.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOfficers();
  }, []);

  const filteredOfficers = officers.filter((o) => {
    if (statusFilter && o.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        o.name.toLowerCase().includes(q) ||
        o.username.toLowerCase().includes(q) ||
        o.jurisdiction.toLowerCase().includes(q) ||
        o.email.toLowerCase().includes(q)
      );
    }
    return true;
  });

  // Calculate aggregates
  const totalAssigned = officers.reduce((sum, o) => sum + o.workload.assigned_cases, 0);
  const totalPending = officers.reduce((sum, o) => sum + o.workload.pending_cases, 0);
  const totalResolved = officers.reduce((sum, o) => sum + o.workload.resolved_cases, 0);
  const activeCount = officers.filter((o) => o.status === "ACTIVE").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1c2d38] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Revenue Officer Oversight</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#00684a] text-[#c3f0d2] font-mono font-semibold">
              ROLE: REVENUE_OFFICER
            </span>
          </div>
          <p className="text-sm text-[#7c8c9a] mt-1">
            Monitor institutional case assignment, jurisdictional allocations, and resolution velocity across Revenue Officers.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/admin/users"
            className="px-4 py-2 rounded-xl bg-[#00283b] border border-[#1c2d38] text-xs font-semibold text-[#c1ccd6] hover:text-white hover:border-[#00ed64]/40 transition-colors flex items-center gap-2"
          >
            <span>👥</span>
            <span>Manage All Users</span>
          </Link>
          <button
            onClick={loadOfficers}
            className="px-4 py-2 rounded-xl bg-[#1c2d38] text-xs font-mono text-[#c1ccd6] hover:text-white hover:bg-[#253947] transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Active Officers</span>
          <div className="text-2xl font-bold text-white mt-1">
            {activeCount} <span className="text-xs font-normal text-[#5c6c7a]">/ {total}</span>
          </div>
          <p className="text-[11px] text-[#00ed64] mt-1 flex items-center gap-1">
            <span>●</span> Revenue authority staff
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Total Assigned Cases</span>
          <div className="text-2xl font-bold text-white mt-1">{totalAssigned}</div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Across all jurisdictions</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Pending Review</span>
          <div className="text-2xl font-bold text-[#f5a623] mt-1">{totalPending}</div>
          <p className="text-[11px] text-[#f5a623] mt-1 flex items-center gap-1">
            <span>⏳</span> Awaiting adjudication
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Resolved Cases</span>
          <div className="text-2xl font-bold text-[#00ed64] mt-1">{totalResolved}</div>
          <p className="text-[11px] text-[#00ed64] mt-1 flex items-center gap-1">
            <span>✓</span> Official decisions recorded
          </p>
        </div>
      </div>

      {/* Governance Notice */}
      <div className="p-4 rounded-xl bg-[#00283b]/60 border border-[#00684a]/30 flex items-start gap-3 text-xs leading-relaxed text-[#c1ccd6]">
        <span className="text-lg">⚖️</span>
        <div>
          <span className="font-bold text-white block mb-0.5">Statutory Boundary & Decision Separation:</span>
          Revenue Officers hold sole decision-making authority over parcel discrepancies, title mutations, and dispute resolutions.
          Administrators govern account status and assignment velocity, but <strong className="text-[#00ed64]">never override official land adjudications without an audit record</strong>.
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38] flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Search by name, username, jurisdiction, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white placeholder-[#5c6c7a] focus:outline-none focus:border-[#00ed64]"
          />
          <span className="absolute left-3 top-2.5 text-xs text-[#5c6c7a]">🔍</span>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white focus:outline-none focus:border-[#00ed64]"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="DEACTIVATED">DEACTIVATED</option>
          </select>

          {search || statusFilter ? (
            <button
              onClick={() => {
                setSearch("");
                setStatusFilter("");
              }}
              className="px-3 py-2 text-xs text-[#7c8c9a] hover:text-white"
            >
              Reset
            </button>
          ) : null}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-xs text-[#fa6e39] flex items-center justify-between">
          <span>{error}</span>
          <button onClick={loadOfficers} className="font-bold underline ml-2">
            Retry
          </button>
        </div>
      )}

      {/* Officers Table */}
      <div className="rounded-xl bg-[#00283b] border border-[#1c2d38] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#001e2b] border-b border-[#1c2d38] text-[#7c8c9a] font-mono uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-5 py-3">Officer Name & ID</th>
                <th className="px-5 py-3">Jurisdiction</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Assigned Workload</th>
                <th className="px-5 py-3">Resolution Velocity</th>
                <th className="px-5 py-3">Last Active</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c2d38]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a] font-mono">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
                      <span>Loading Revenue Officer Roster...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredOfficers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a]">
                    No Revenue Officers found matching current criteria.
                  </td>
                </tr>
              ) : (
                filteredOfficers.map((officer) => {
                  const assigned = officer.workload.assigned_cases;
                  const pending = officer.workload.pending_cases;
                  const resolved = officer.workload.resolved_cases;
                  const resolutionPct = assigned > 0 ? Math.round((resolved / assigned) * 100) : 100;

                  return (
                    <tr key={officer.id} className="hover:bg-[#002233] transition-colors">
                      {/* Name & ID */}
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-[#00684a] text-[#00ed64] flex items-center justify-center font-bold font-mono text-xs">
                            {officer.name.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-semibold text-white">{officer.name}</div>
                            <div className="text-[11px] text-[#7c8c9a] font-mono flex items-center gap-2">
                              <span>@{officer.username}</span>
                              <span>•</span>
                              <span>{officer.id}</span>
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Jurisdiction */}
                      <td className="px-5 py-4">
                        <span className="px-2.5 py-1 rounded bg-[#001e2b] border border-[#1c2d38] font-mono text-[11px] text-[#c1ccd6]">
                          {officer.jurisdiction || "Statewide Pool"}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="px-5 py-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider ${
                            officer.status === "ACTIVE"
                              ? "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                              : "bg-[#fa6e39]/10 text-[#fa6e39] border border-[#fa6e39]/20"
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${officer.status === "ACTIVE" ? "bg-[#00ed64]" : "bg-[#fa6e39]"}`} />
                          {officer.status}
                        </span>
                      </td>

                      {/* Workload */}
                      <td className="px-5 py-4 font-mono">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-white font-bold">{assigned} total</span>
                          <span className="text-[#7c8c9a]">({pending} pending)</span>
                        </div>
                        <div className="w-32 bg-[#001e2b] h-1.5 rounded-full mt-1.5 overflow-hidden flex">
                          <div
                            className="bg-[#00ed64] h-full"
                            style={{ width: `${resolutionPct}%` }}
                            title={`${resolved} resolved`}
                          />
                          <div
                            className="bg-[#f5a623] h-full"
                            style={{ width: `${100 - resolutionPct}%` }}
                            title={`${pending} pending`}
                          />
                        </div>
                      </td>

                      {/* Resolution Velocity */}
                      <td className="px-5 py-4 font-mono">
                        <span className="text-xs text-[#00ed64] font-semibold">{resolutionPct}%</span>
                        <span className="text-[10px] text-[#7c8c9a] block">
                          {resolved} of {assigned} cases
                        </span>
                      </td>

                      {/* Last Active */}
                      <td className="px-5 py-4 text-[#7c8c9a] font-mono text-[11px]">
                        {officer.last_login ? new Date(officer.last_login).toLocaleDateString() : "Never"}
                      </td>

                      {/* Actions */}
                      <td className="px-5 py-4 text-right">
                        <Link
                          href={`/admin/review-cases?search=${encodeURIComponent(officer.username)}`}
                          className="px-3 py-1.5 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-xs font-semibold text-[#00ed64] hover:bg-[#00684a]/20 transition-colors"
                        >
                          Inspect Cases →
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer info */}
        <div className="p-4 bg-[#001e2b] border-t border-[#1c2d38] flex flex-col sm:flex-row items-center justify-between text-xs text-[#7c8c9a] font-mono gap-2">
          <span>Showing {filteredOfficers.length} of {total} registered revenue officers</span>
          <span className="text-[11px]">Jurisdiction allocation managed according to Karnataka Land Revenue Act (Advisory Demo Model)</span>
        </div>
      </div>
    </div>
  );
}
