"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAdmin } from "../adminAuth";

interface DashboardData {
  status: string;
  timestamp: string;
  mode: string;
  overview: {
    total_users: number;
    active_officers: number;
    pending_review_cases: number;
    documents_processed: number;
    validation_events: number;
    administrative_events: number;
    parcels_indexed: number;
  };
  system_health: {
    api: string;
    database: string;
    storage: string;
    document_ai: string;
    gis_engine: string;
  };
  recent_actions: Array<{
    id: string;
    action_type: string;
    actor_id: string;
    target_resource_type: string;
    target_resource_id: string;
    reason: string;
    status: string;
    created_at: string;
  }>;
}

export default function AdminDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAdmin("/api/v1/admin/dashboard");
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err?.message || "Failed to load administrator dashboard telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Title & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1c2d38] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-white tracking-tight">Platform Operations & Governance</h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#00684a] text-[#c3f0d2] font-semibold">
              Live Telemetry
            </span>
          </div>
          <p className="text-xs text-[#7c8c9a]">
            System-wide operational oversight, workload allocation, and immutable audit logs under SIH26018 rules.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 rounded-full bg-[#1c2d38] hover:bg-[#253947] text-white text-xs font-mono transition-colors border border-[#3d4f5b] flex items-center gap-2 self-start"
        >
          <span>🔄</span>
          <span>{loading ? "Refreshing..." : "Refresh Metrics"}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={loadData} className="underline font-bold">
            Retry Connection
          </button>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: "Total Users", value: data?.overview.total_users ?? "—", icon: "👥", color: "#00ed64" },
          { label: "Active Officers", value: data?.overview.active_officers ?? "—", icon: "🏛️", color: "#3d4f9f" },
          { label: "Pending Cases", value: data?.overview.pending_review_cases ?? "—", icon: "⚖️", color: "#fa6e39" },
          { label: "Documents", value: data?.overview.documents_processed ?? "—", icon: "📄", color: "#c1ccd6" },
          { label: "Validation Events", value: data?.overview.validation_events ?? "—", icon: "🔍", color: "#7b3ff2" },
          { label: "Admin Actions", value: data?.overview.administrative_events ?? "—", icon: "📜", color: "#00a35c" },
        ].map((card, i) => (
          <div key={i} className="bg-[#00283b] border border-[#1c2d38] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-[#7c8c9a] mb-2 font-mono">
              <span>{card.label}</span>
              <span className="text-base">{card.icon}</span>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">{card.value}</div>
          </div>
        ))}
      </div>

      {/* Subsystem Health Monitor & Quick Links Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health */}
        <div className="lg:col-span-1 bg-[#00283b] border border-[#1c2d38] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4 border-b border-[#1c2d38] pb-3">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span>🛡️</span>
              <span>Subsystem Health Probes</span>
            </h2>
            <span className="text-[10px] font-mono text-[#00ed64]">100% Deterministic</span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            {[
              { label: "Core FastAPI Service", key: "api", status: data?.system_health.api },
              { label: "Relational Database (SQLAlchemy)", key: "database", status: data?.system_health.database },
              { label: "Evidence Vault (Local WORM)", key: "storage", status: data?.system_health.storage },
              { label: "Document AI Engine", key: "document_ai", status: data?.system_health.document_ai },
              { label: "GIS Geodesic Engine", key: "gis_engine", status: data?.system_health.gis_engine },
            ].map((sub, i) => {
              const isHealthy = sub.status === "healthy";
              return (
                <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-[#001e2b] border border-[#1c2d38]">
                  <span className="text-[#c1ccd6]">{sub.label}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      isHealthy
                        ? "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                        : "bg-[#fa6e39]/10 text-[#fa6e39] border border-[#fa6e39]/20"
                    }`}
                  >
                    {sub.status ? sub.status.toUpperCase() : "CHECKING"}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="mt-4 pt-3 border-t border-[#1c2d38] text-[11px] text-[#5c6c7a] font-mono">
            Environment: <span className="text-[#c1ccd6]">{data?.mode || "DEVELOPMENT"}</span>
          </div>
        </div>

        {/* Quick Governance Navigation */}
        <div className="lg:col-span-2 bg-[#00283b] border border-[#1c2d38] rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-[#1c2d38] pb-3">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <span>⚡</span>
                <span>Governance Control Portals</span>
              </h2>
              <span className="text-[10px] font-mono text-[#7c8c9a]">Role-Enforced Actions</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link
                href="/admin/users"
                className="p-4 rounded-xl bg-[#001e2b] hover:bg-[#00344a] border border-[#1c2d38] hover:border-[#00ed64]/40 transition-all group"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-[#3d4f9f]/20 text-[#3d4f9f] flex items-center justify-center text-lg">
                    👥
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#00ed64] transition-colors">
                    User Accounts
                  </h3>
                </div>
                <p className="text-xs text-[#7c8c9a] leading-relaxed">
                  Search, create, activate, or deactivate citizen and officer accounts with required audit justification.
                </p>
              </Link>

              <Link
                href="/admin/officers"
                className="p-4 rounded-xl bg-[#001e2b] hover:bg-[#00344a] border border-[#1c2d38] hover:border-[#00ed64]/40 transition-all group"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-[#7b3ff2]/20 text-[#7b3ff2] flex items-center justify-center text-lg">
                    🏛️
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#00ed64] transition-colors">
                    Revenue Officers
                  </h3>
                </div>
                <p className="text-xs text-[#7c8c9a] leading-relaxed">
                  Inspect assigned workloads, pending case distribution, and jurisdictional coverage across taluks.
                </p>
              </Link>

              <Link
                href="/admin/review-cases"
                className="p-4 rounded-xl bg-[#001e2b] hover:bg-[#00344a] border border-[#1c2d38] hover:border-[#00ed64]/40 transition-all group"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-[#fa6e39]/20 text-[#fa6e39] flex items-center justify-center text-lg">
                    ⚖️
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#00ed64] transition-colors">
                    Review Cases Oversight
                  </h3>
                </div>
                <p className="text-xs text-[#7c8c9a] leading-relaxed">
                  Examine system-wide parcel variance cases, priority levels, and officer decision notes.
                </p>
              </Link>

              <Link
                href="/admin/audit"
                className="p-4 rounded-xl bg-[#001e2b] hover:bg-[#00344a] border border-[#1c2d38] hover:border-[#00ed64]/40 transition-all group"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-[#00ed64]/20 text-[#00ed64] flex items-center justify-center text-lg">
                    📜
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#00ed64] transition-colors">
                    Tamper-Evident Audit
                  </h3>
                </div>
                <p className="text-xs text-[#7c8c9a] leading-relaxed">
                  Query the append-only cryptographic event log. Inspect before/after state diffs and actor timestamps.
                </p>
              </Link>
            </div>
          </div>

          {/* Governance Notice */}
          <div className="mt-4 p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-[11px] text-[#7c8c9a] font-mono flex items-center gap-2">
            <span>ℹ️</span>
            <span>
              <strong>Rule 4 & Rule 7 Compliance:</strong> Administrators oversee platform integrity and account governance. Authorized revenue officers adjudicate official review cases.
            </span>
          </div>
        </div>
      </div>

      {/* Recent Governed Administrative Actions Table */}
      <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4 border-b border-[#1c2d38] pb-3">
          <div>
            <h2 className="text-sm font-bold text-white">Recent Governed Administrative Events</h2>
            <p className="text-xs text-[#7c8c9a]">Latest actions executed by authorized administrators</p>
          </div>
          <Link
            href="/admin/audit"
            className="text-xs text-[#00ed64] hover:underline font-mono"
          >
            View Full Audit Trail →
          </Link>
        </div>

        {data?.recent_actions && data.recent_actions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#1c2d38] text-[#5c6c7a] uppercase text-[10px]">
                  <th className="py-2.5 px-3">Action Type</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Target Resource</th>
                  <th className="py-2.5 px-3">Reason / Justification</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c2d38] text-[#c1ccd6]">
                {data.recent_actions.map((act) => (
                  <tr key={act.id} className="hover:bg-[#001e2b] transition-colors">
                    <td className="py-3 px-3 text-[#00ed64] font-semibold">{act.action_type}</td>
                    <td className="py-3 px-3 text-white">{act.actor_id}</td>
                    <td className="py-3 px-3">
                      <span className="px-1.5 py-0.5 rounded bg-[#1c2d38] text-[10px]">
                        {act.target_resource_type}:{act.target_resource_id}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#7c8c9a] max-w-xs truncate" title={act.reason}>
                      {act.reason}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20">
                        {act.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#5c6c7a] whitespace-nowrap">
                      {new Date(act.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-[#5c6c7a] font-mono">
            No administrative events recorded yet in this environment.
          </div>
        )}
      </div>
    </div>
  );
}
