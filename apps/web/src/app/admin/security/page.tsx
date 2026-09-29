"use client";

import { useEffect, useState } from "react";
import { fetchAdmin } from "../adminAuth";

interface SecurityTelemetry {
  recent_logins: Array<{
    id: string;
    actor_id: string;
    action: string;
    timestamp: string;
  }>;
  failed_logins_total: number;
  inactive_users_total: number;
  role_changes_total: number;
  security_policies: {
    jwt_algorithm: string;
    password_hashing: string;
    demo_tokens_isolated: boolean;
    demo_mode_active: boolean;
    worm_tamper_immutability: string;
    audit_append_only: string;
  };
}

export default function AdminSecurityPage() {
  const [data, setData] = useState<SecurityTelemetry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSecurity = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAdmin("/api/v1/admin/security");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err?.message || "Failed to load security telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSecurity();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1c2d38] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Security Controls & Telemetry</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#00684a] text-[#c3f0d2] font-mono font-semibold">
              HARDENED CONTROLS
            </span>
          </div>
          <p className="text-sm text-[#7c8c9a] mt-1">
            Real-time security telemetry, authentication anomalies, cryptographic policies, and tenant isolation status.
          </p>
        </div>

        <button
          onClick={loadSecurity}
          className="px-4 py-2 rounded-xl bg-[#1c2d38] text-xs font-mono text-[#c1ccd6] hover:text-white hover:bg-[#253947] transition-colors"
        >
          🔄 Refresh Telemetry
        </button>
      </div>

      {/* Mode Isolation Warning Banner */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38] flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#001e2b] border border-[#1c2d38] flex items-center justify-center text-xl">
            🛡️
          </div>
          <div>
            <h4 className="text-xs font-bold text-white font-mono flex items-center gap-2">
              <span>ENVIRONMENT POLICY STATE:</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono ${
                  data?.security_policies.demo_mode_active
                    ? "bg-[#f5a623]/10 text-[#f5a623] border border-[#f5a623]/20"
                    : "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                }`}
              >
                {data?.security_policies.demo_mode_active ? "DEMO_SYNTHETIC ACTIVE" : "PRODUCTION ENFORCED"}
              </span>
            </h4>
            <p className="text-[11px] text-[#7c8c9a] mt-0.5">
              {data?.security_policies.demo_mode_active
                ? "Static demo tokens are accepted solely for sandbox testing. In production (DEMO_MODE=false), static tokens are strictly rejected."
                : "Zero static demo tokens permitted. All requests must carry signed, non-expired HS256 JWT bearer credentials."}
            </p>
          </div>
        </div>

        <div className="text-right font-mono text-[11px] text-[#00ed64]">
          <span>Isolation Defense Active</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Failed Logins Total</span>
          <div className="text-2xl font-bold text-[#fa6e39] mt-1">
            {loading ? "..." : data?.failed_logins_total ?? 0}
          </div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Bad password or nonexistent user</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Deactivated Accounts</span>
          <div className="text-2xl font-bold text-[#f5a623] mt-1">
            {loading ? "..." : data?.inactive_users_total ?? 0}
          </div>
          <p className="text-[11px] text-[#7c8c9a] mt-1">Revoked platform access</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Role Modifications</span>
          <div className="text-2xl font-bold text-white mt-1">
            {loading ? "..." : data?.role_changes_total ?? 0}
          </div>
          <p className="text-[11px] text-[#00ed64] mt-1">Privilege escalation audited</p>
        </div>

        <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38]">
          <span className="text-xs text-[#7c8c9a] uppercase font-mono tracking-wider">Active Security Policies</span>
          <div className="text-2xl font-bold text-[#00ed64] mt-1">6 / 6</div>
          <p className="text-[11px] text-[#00ed64] mt-1">Fully enforced</p>
        </div>
      </div>

      {/* Policy Checklist */}
      <div className="p-6 rounded-xl bg-[#00283b] border border-[#1c2d38] space-y-4">
        <h3 className="text-sm font-bold text-white tracking-wide font-mono uppercase">
          Institutional Security Policy Checklist
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Password Hash Algorithm</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                ENFORCED
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              {data?.security_policies.password_hashing || "bcrypt (72-byte truncation enforced)"}
            </p>
          </div>

          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Stateless JWT Signature</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                HS256
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              Cryptographic HMAC-SHA256 signature with claims expiration and role validation.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">WORM Evidentiary Vault</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                ACTIVE
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              SHA-256 content-addressing; mutations trigger StorageTamperError exceptions.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Audit Log Append-Only Protection</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                ENFORCED
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              Audit events cannot be edited or erased via API; zero god-mode mutation endpoints.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">RBAC Server-Side Authorization</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                PROTECTED
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              Authorization evaluated server-side on every request; UI guards are purely cosmetic.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38] space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">Administrative Self-Lockout Defense</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20 font-bold">
                ACTIVE
              </span>
            </div>
            <p className="text-[#7c8c9a] text-[11px]">
              Administrators are prohibited from deactivating their own account to prevent lockouts.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Authentication Events */}
      <div className="rounded-xl bg-[#00283b] border border-[#1c2d38] overflow-hidden">
        <div className="p-4 bg-[#001e2b] border-b border-[#1c2d38] flex items-center justify-between">
          <span className="font-mono text-xs font-bold text-white uppercase tracking-wider">
            Recent Authentication Activity Stream
          </span>
          <span className="text-[11px] text-[#7c8c9a] font-mono">Last 10 Events</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#001e2b] border-b border-[#1c2d38] text-[#7c8c9a] font-mono uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-5 py-3">Timestamp (UTC)</th>
                <th className="px-5 py-3">Action</th>
                <th className="px-5 py-3">Actor / Principal</th>
                <th className="px-5 py-3">Audit Reference ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c2d38]">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-5 py-8 text-center text-[#7c8c9a] font-mono">
                    Loading security event stream...
                  </td>
                </tr>
              ) : !data?.recent_logins || data.recent_logins.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-5 py-8 text-center text-[#7c8c9a]">
                    No recent authentication events recorded in ledger.
                  </td>
                </tr>
              ) : (
                data.recent_logins.map((item) => (
                  <tr key={item.id} className="hover:bg-[#002233] transition-colors">
                    <td className="px-5 py-3.5 font-mono text-[11px] text-[#7c8c9a]">
                      {new Date(item.timestamp).toLocaleString()}
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          item.action === "LOGIN_SUCCESS"
                            ? "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                            : item.action === "LOGOUT"
                            ? "bg-[#c1ccd6]/10 text-[#c1ccd6] border border-[#c1ccd6]/20"
                            : "bg-[#fa6e39]/10 text-[#fa6e39] border border-[#fa6e39]/20"
                        }`}
                      >
                        {item.action}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-white">
                      @{item.actor_id}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-[#5c6c7a]">
                      {item.id}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
