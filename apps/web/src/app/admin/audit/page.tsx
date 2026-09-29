"use client";

import { useEffect, useState } from "react";
import { fetchAdmin } from "../adminAuth";

interface AuditEvent {
  id: string;
  actor_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  timestamp: string;
  before_state?: any;
  after_state?: any;
  reason?: string;
  trace_id?: string;
}

interface AdminAction {
  id: string;
  action_type: string;
  actor_id: string;
  actor_role: string;
  target_resource_type: string;
  target_resource_id: string;
  reason: string;
  before_state?: any;
  after_state?: any;
  status: string;
  created_at: string;
}

export default function AdminAuditPage() {
  const [activeTab, setActiveTab] = useState<"system" | "admin_actions">("system");

  // System audit trail
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [eventsTotal, setEventsTotal] = useState(0);
  const [eventsLoading, setEventsLoading] = useState(true);

  // Governed admin actions
  const [actions, setActions] = useState<AdminAction[]>([]);
  const [actionsTotal, setActionsTotal] = useState(0);
  const [actionsLoading, setActionsLoading] = useState(false);

  // Filters
  const [actorFilter, setActorFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [entityFilter, setEntityFilter] = useState("");

  // Diff Inspector Modal
  const [inspectItem, setInspectItem] = useState<{
    title: string;
    actor: string;
    timestamp: string;
    reason?: string;
    before?: any;
    after?: any;
  } | null>(null);

  const loadAuditEvents = async () => {
    setEventsLoading(true);
    try {
      const params = new URLSearchParams();
      if (actorFilter) params.append("actor_id", actorFilter);
      if (actionFilter) params.append("action", actionFilter);
      if (entityFilter) params.append("entity_type", entityFilter);

      const res = await fetchAdmin(`/api/v1/admin/audit?${params.toString()}`);
      if (res.ok) {
        const json = await res.json();
        setEvents(json.events || []);
        setEventsTotal(json.total || 0);
      }
    } catch {
      // Ignore error for offline resilience
    } finally {
      setEventsLoading(false);
    }
  };

  const loadAdminActions = async () => {
    setActionsLoading(true);
    try {
      const params = new URLSearchParams();
      if (actionFilter) params.append("action_type", actionFilter);
      if (actorFilter) params.append("actor_id", actorFilter);

      const res = await fetchAdmin(`/api/v1/admin/actions?${params.toString()}`);
      if (res.ok) {
        const json = await res.json();
        setActions(json.actions || []);
        setActionsTotal(json.total || 0);
      }
    } catch {
      // Ignore
    } finally {
      setActionsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "system") {
      loadAuditEvents();
    } else {
      loadAdminActions();
    }
  }, [activeTab, actionFilter, entityFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1c2d38] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Audit & Governance Ledger</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#00684a] text-[#c3f0d2] font-mono font-semibold">
              SHA-256 WORM
            </span>
          </div>
          <p className="text-sm text-[#7c8c9a] mt-1">
            Tamper-evident, non-repudiable audit logs recording all state mutations, security events, and administrative decisions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => (activeTab === "system" ? loadAuditEvents() : loadAdminActions())}
            className="px-4 py-2 rounded-xl bg-[#1c2d38] text-xs font-mono text-[#c1ccd6] hover:text-white hover:bg-[#253947] transition-colors"
          >
            🔄 Refresh Ledger
          </button>
        </div>
      </div>

      {/* Tamper Evidence Banner */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#00ed64]/30 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#00684a]/30 border border-[#00ed64]/40 flex items-center justify-center text-lg text-[#00ed64]">
            🔒
          </div>
          <div>
            <h4 className="text-xs font-bold text-white font-mono flex items-center gap-2">
              <span>WORM IMMUTABILITY LEDGER (RULE 11 COMPLIANT)</span>
              <span className="w-2 h-2 rounded-full bg-[#00ed64] animate-pulse" />
            </h4>
            <p className="text-[11px] text-[#7c8c9a] mt-0.5">
              Append-only storage with cryptographic proof. Silent deletions or alterations trigger unhandled exception flags.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px] text-[#c1ccd6] bg-[#001e2b] px-3 py-1.5 rounded-lg border border-[#1c2d38]">
          <span className="text-[#00ed64]">Indexed Records:</span>
          <span>{activeTab === "system" ? eventsTotal : actionsTotal}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#1c2d38] gap-4">
        <button
          onClick={() => {
            setActiveTab("system");
            setActionFilter("");
          }}
          className={`pb-3 text-xs font-semibold tracking-wide border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "system"
              ? "border-[#00ed64] text-[#00ed64]"
              : "border-transparent text-[#7c8c9a] hover:text-white"
          }`}
        >
          <span>📜</span>
          <span>System Audit Trail ({eventsTotal})</span>
        </button>

        <button
          onClick={() => {
            setActiveTab("admin_actions");
            setActionFilter("");
          }}
          className={`pb-3 text-xs font-semibold tracking-wide border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "admin_actions"
              ? "border-[#00ed64] text-[#00ed64]"
              : "border-transparent text-[#7c8c9a] hover:text-white"
          }`}
        >
          <span>⚖️</span>
          <span>Governed Admin Actions ({actionsTotal})</span>
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-xl bg-[#00283b] border border-[#1c2d38] flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="flex-1 flex gap-2">
          <input
            type="text"
            placeholder="Filter by Actor ID (e.g. admin, officer, or user ID)..."
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white placeholder-[#5c6c7a] focus:outline-none focus:border-[#00ed64]"
          />
          <button
            onClick={() => (activeTab === "system" ? loadAuditEvents() : loadAdminActions())}
            className="px-4 py-2 rounded-xl bg-[#00684a] text-white text-xs font-bold font-mono"
          >
            Apply
          </button>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === "system" && (
            <select
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
              className="px-3 py-2 rounded-xl bg-[#001e2b] border border-[#1c2d38] text-xs text-white focus:outline-none focus:border-[#00ed64]"
            >
              <option value="">All Entities</option>
              <option value="USER">USER</option>
              <option value="PARCEL">PARCEL</option>
              <option value="REVIEW_CASE">REVIEW_CASE</option>
              <option value="DOCUMENT">DOCUMENT</option>
              <option value="AUTH">AUTH</option>
            </select>
          )}

          {(actorFilter || actionFilter || entityFilter) && (
            <button
              onClick={() => {
                setActorFilter("");
                setActionFilter("");
                setEntityFilter("");
              }}
              className="px-3 py-2 text-xs text-[#7c8c9a] hover:text-white"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Tab 1: System Audit Trail */}
      {activeTab === "system" && (
        <div className="rounded-xl bg-[#00283b] border border-[#1c2d38] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#001e2b] border-b border-[#1c2d38] text-[#7c8c9a] font-mono uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3">Timestamp (UTC)</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">Actor</th>
                  <th className="px-5 py-3">Entity Reference</th>
                  <th className="px-5 py-3">Justification Reason</th>
                  <th className="px-5 py-3 text-right">State Diff</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c2d38]">
                {eventsLoading ? (
                  <tr>
                    <td colSpan={6} className="px-5 py-12 text-center text-[#7c8c9a] font-mono">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
                        <span>Querying immutable WORM log...</span>
                      </div>
                    </td>
                  </tr>
                ) : events.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-5 py-12 text-center text-[#7c8c9a]">
                      No audit events recorded matching current criteria.
                    </td>
                  </tr>
                ) : (
                  events.map((e) => (
                    <tr key={e.id} className="hover:bg-[#002233] transition-colors">
                      <td className="px-5 py-4 font-mono text-[11px] text-[#7c8c9a] whitespace-nowrap">
                        {new Date(e.timestamp).toLocaleString()}
                        <span className="block text-[9px] text-[#5c6c7a]">{e.id.slice(0, 16)}...</span>
                      </td>

                      <td className="px-5 py-4">
                        <span className="px-2.5 py-1 rounded bg-[#001e2b] border border-[#1c2d38] font-mono text-[11px] text-[#00ed64] font-bold">
                          {e.action}
                        </span>
                      </td>

                      <td className="px-5 py-4 font-mono text-xs text-white">
                        @{e.actor_id}
                      </td>

                      <td className="px-5 py-4 font-mono text-xs text-[#c1ccd6]">
                        <span className="text-[10px] text-[#7c8c9a] block">{e.entity_type}</span>
                        {e.entity_id}
                      </td>

                      <td className="px-5 py-4 text-[#c1ccd6] max-w-xs truncate">
                        {e.reason || <span className="text-[#5c6c7a] italic">None stated</span>}
                      </td>

                      <td className="px-5 py-4 text-right">
                        {(e.before_state || e.after_state) ? (
                          <button
                            onClick={() =>
                              setInspectItem({
                                title: `Audit Event: ${e.action}`,
                                actor: e.actor_id,
                                timestamp: e.timestamp,
                                reason: e.reason,
                                before: e.before_state,
                                after: e.after_state,
                              })
                            }
                            className="px-3 py-1 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-[11px] font-mono text-[#00ed64] hover:bg-[#00684a]/20 transition-colors"
                          >
                            Inspect Diff 🔍
                          </button>
                        ) : (
                          <span className="text-[10px] font-mono text-[#5c6c7a]">—</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Governed Administrative Actions */}
      {activeTab === "admin_actions" && (
        <div className="rounded-xl bg-[#00283b] border border-[#1c2d38] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#001e2b] border-b border-[#1c2d38] text-[#7c8c9a] font-mono uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3">Timestamp (UTC)</th>
                  <th className="px-5 py-3">Action Type</th>
                  <th className="px-5 py-3">Admin Actor</th>
                  <th className="px-5 py-3">Target Resource</th>
                  <th className="px-5 py-3">Mandatory Justification</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c2d38]">
                {actionsLoading ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a] font-mono">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
                        <span>Querying administrative ledger...</span>
                      </div>
                    </td>
                  </tr>
                ) : actions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-12 text-center text-[#7c8c9a]">
                      No administrative actions logged yet.
                    </td>
                  </tr>
                ) : (
                  actions.map((a) => (
                    <tr key={a.id} className="hover:bg-[#002233] transition-colors">
                      <td className="px-5 py-4 font-mono text-[11px] text-[#7c8c9a] whitespace-nowrap">
                        {new Date(a.created_at).toLocaleString()}
                      </td>

                      <td className="px-5 py-4 font-mono font-bold text-white">
                        <span className="px-2.5 py-1 rounded bg-[#001e2b] border border-[#1c2d38] text-[#f5a623]">
                          {a.action_type}
                        </span>
                      </td>

                      <td className="px-5 py-4 font-mono text-xs text-white">
                        @{a.actor_id}
                        <span className="block text-[10px] text-[#7c8c9a]">{a.actor_role}</span>
                      </td>

                      <td className="px-5 py-4 font-mono text-xs text-[#c1ccd6]">
                        <span className="text-[10px] text-[#7c8c9a] block">{a.target_resource_type}</span>
                        {a.target_resource_id}
                      </td>

                      <td className="px-5 py-4 text-[#c1ccd6] max-w-xs truncate">
                        <span title={a.reason}>{a.reason}</span>
                      </td>

                      <td className="px-5 py-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20">
                          {a.status}
                        </span>
                      </td>

                      <td className="px-5 py-4 text-right">
                        <button
                          onClick={() =>
                            setInspectItem({
                              title: `Governed Action: ${a.action_type}`,
                              actor: a.actor_id,
                              timestamp: a.created_at,
                              reason: a.reason,
                              before: a.before_state,
                              after: a.after_state,
                            })
                          }
                          className="px-3 py-1 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-[11px] font-mono text-[#00ed64] hover:bg-[#00684a]/20 transition-colors"
                        >
                          Payload 🔍
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Diff Inspector Modal */}
      {inspectItem && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#1c2d38] pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#00ed64]">State Delta Inspector</span>
                <h3 className="text-lg font-bold text-white">{inspectItem.title}</h3>
                <p className="text-[11px] text-[#7c8c9a] font-mono">
                  Actor: @{inspectItem.actor} • {new Date(inspectItem.timestamp).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => setInspectItem(null)}
                className="w-8 h-8 rounded-full bg-[#1c2d38] text-[#7c8c9a] hover:text-white flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            {/* Justification Reason */}
            {inspectItem.reason && (
              <div className="p-3 rounded-xl bg-[#001e2b] border border-[#1c2d38]">
                <span className="text-[10px] font-mono uppercase text-[#7c8c9a] block mb-1">
                  Recorded Audit Justification
                </span>
                <p className="text-xs text-white font-mono">{inspectItem.reason}</p>
              </div>
            )}

            {/* Side-by-Side Diffs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#fa6e39] uppercase font-bold">
                  ◄ Before State
                </span>
                <pre className="p-3 rounded-xl bg-[#001824] border border-[#1c2d38] text-[11px] font-mono text-[#fa6e39] overflow-x-auto max-h-60">
                  {inspectItem.before ? JSON.stringify(inspectItem.before, null, 2) : "null (No prior state)"}
                </pre>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#00ed64] uppercase font-bold">
                  ► After State / Payload
                </span>
                <pre className="p-3 rounded-xl bg-[#001824] border border-[#1c2d38] text-[11px] font-mono text-[#00ed64] overflow-x-auto max-h-60">
                  {inspectItem.after ? JSON.stringify(inspectItem.after, null, 2) : "null (Empty payload)"}
                </pre>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-[#1c2d38]">
              <button
                onClick={() => setInspectItem(null)}
                className="px-4 py-2 rounded-xl bg-[#00684a] text-white text-xs font-bold hover:bg-[#00ed64] hover:text-[#001e2b] transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
