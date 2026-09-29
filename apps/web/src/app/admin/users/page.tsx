"use client";

import { useEffect, useState } from "react";
import { fetchAdmin, getAdminUser } from "../adminAuth";

interface UserItem {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
  status: string;
  jurisdiction?: string;
  phone?: string;
  last_login?: string;
  created_at?: string;
}

export default function AdminUsersPage() {
  const adminUser = getAdminUser();

  const [users, setUsers] = useState<UserItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusModalUser, setStatusModalUser] = useState<UserItem | null>(null);
  const [roleModalUser, setRoleModalUser] = useState<UserItem | null>(null);
  const [reasonInput, setReasonInput] = useState("");
  const [newRoleSelect, setNewRoleSelect] = useState("citizen");
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  // Create form state
  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    name: "",
    role: "citizen",
    password: "",
    jurisdiction: "",
    phone: "",
  });

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (roleFilter) params.append("role", roleFilter);
      if (statusFilter) params.append("status", statusFilter);

      const res = await fetchAdmin(`/api/v1/admin/users?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setUsers(json.users || []);
      setTotal(json.total || 0);
    } catch (err: any) {
      setError(err?.message || "Failed to load user roster.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [roleFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadUsers();
  };

  const handleStatusToggle = async () => {
    if (!statusModalUser || !reasonInput.trim()) {
      setModalError("A mandatory justification reason is required for account status modifications.");
      return;
    }

    setModalSubmitting(true);
    setModalError(null);
    try {
      const targetStatus = statusModalUser.status === "ACTIVE" ? "DEACTIVATED" : "ACTIVE";
      const res = await fetchAdmin(`/api/v1/admin/users/${statusModalUser.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: targetStatus, reason: reasonInput.trim() }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || "Status modification failed.");
      }

      setStatusModalUser(null);
      setReasonInput("");
      loadUsers();
    } catch (err: any) {
      setModalError(err?.message || "Operation failed.");
    } finally {
      setModalSubmitting(false);
    }
  };

  const handleRoleChange = async () => {
    if (!roleModalUser || !reasonInput.trim()) {
      setModalError("A mandatory justification reason is required for role modification.");
      return;
    }

    setModalSubmitting(true);
    setModalError(null);
    try {
      const res = await fetchAdmin(`/api/v1/admin/users/${roleModalUser.id}/role`, {
        method: "PATCH",
        body: JSON.stringify({ role: newRoleSelect, reason: reasonInput.trim() }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || "Role modification failed.");
      }

      setRoleModalUser(null);
      setReasonInput("");
      loadUsers();
    } catch (err: any) {
      setModalError(err?.message || "Operation failed.");
    } finally {
      setModalSubmitting(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalSubmitting(true);
    setModalError(null);

    try {
      const res = await fetchAdmin("/api/v1/admin/users", {
        method: "POST",
        body: JSON.stringify(newUser),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || "User creation failed.");
      }

      setShowCreateModal(false);
      setNewUser({
        username: "",
        email: "",
        name: "",
        role: "citizen",
        password: "",
        jurisdiction: "",
        phone: "",
      });
      loadUsers();
    } catch (err: any) {
      setModalError(err?.message || "Creation failed.");
    } finally {
      setModalSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1c2d38] pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">User Account Governance</h1>
          <p className="text-xs text-[#7c8c9a] mt-0.5">
            Administer citizen, officer, and administrator credentials, account activation, and role assignments.
          </p>
        </div>

        <button
          onClick={() => {
            setShowCreateModal(true);
            setModalError(null);
          }}
          className="px-4 py-2.5 rounded-full bg-[#00ed64] hover:bg-[#00b545] text-[#001e2b] font-bold text-xs tracking-wide transition-all shadow-md flex items-center gap-2 self-start"
        >
          <span>➕</span>
          <span>Provision New User</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#00283b] border border-[#1c2d38] rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex gap-2">
          <input
            type="text"
            placeholder="Search by name, email, or username..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3.5 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64] placeholder:text-[#5c6c7a]"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-[#1c2d38] hover:bg-[#253947] text-white text-xs font-mono transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex gap-2 w-full md:w-auto font-mono text-xs">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-[#c1ccd6] focus:outline-none focus:border-[#00ed64]"
          >
            <option value="">All Roles</option>
            <option value="citizen">Citizen</option>
            <option value="revenue_officer">Revenue Officer</option>
            <option value="administrator">Administrator</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-[#c1ccd6] focus:outline-none focus:border-[#00ed64]"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="DEACTIVATED">Deactivated</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs">
          {error}
        </div>
      )}

      {/* Users Table */}
      <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-[#1c2d38] flex items-center justify-between text-xs text-[#7c8c9a] font-mono">
          <span>{total} Total Registered Accounts</span>
          <span>Showing up to 50 entries</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-[#7c8c9a]">
            Loading user records...
          </div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center text-xs font-mono text-[#7c8c9a]">
            No users match the specified criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#1c2d38] text-[#5c6c7a] uppercase text-[10px] bg-[#002232]">
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Jurisdiction</th>
                  <th className="py-3 px-4">Last Activity</th>
                  <th className="py-3 px-4 text-right">Governance Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c2d38] text-[#c1ccd6]">
                {users.map((u) => {
                  const isSelf = adminUser?.id === u.id || adminUser?.username === u.username;
                  const isDeactivated = u.status === "DEACTIVATED";

                  return (
                    <tr key={u.id} className="hover:bg-[#001e2b] transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-white text-xs">{u.name}</div>
                        <div className="text-[11px] text-[#7c8c9a]">{u.email}</div>
                        <div className="text-[10px] text-[#5c6c7a]">{u.username} · {u.id}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                            u.role === "administrator"
                              ? "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                              : u.role === "revenue_officer"
                              ? "bg-[#3d4f9f]/20 text-[#c3f0d2] border border-[#3d4f9f]"
                              : "bg-[#1c2d38] text-[#c1ccd6]"
                          }`}
                        >
                          {u.role.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            isDeactivated
                              ? "bg-[#fa6e39]/10 text-[#fa6e39] border border-[#fa6e39]/30"
                              : "bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20"
                          }`}
                        >
                          {u.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-[#7c8c9a]">
                        {u.jurisdiction || "—"}
                      </td>
                      <td className="py-3.5 px-4 text-[#5c6c7a] whitespace-nowrap">
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-2">
                        {/* Role Change Button */}
                        <button
                          onClick={() => {
                            setRoleModalUser(u);
                            setNewRoleSelect(u.role);
                            setReasonInput("");
                            setModalError(null);
                          }}
                          className="px-2.5 py-1 rounded bg-[#1c2d38] hover:bg-[#253947] text-[#c1ccd6] hover:text-white text-[11px] transition-colors"
                        >
                          Role
                        </button>

                        {/* Status Toggle Button */}
                        <button
                          disabled={isSelf}
                          title={isSelf ? "Self-deactivation is prohibited by policy." : undefined}
                          onClick={() => {
                            setStatusModalUser(u);
                            setReasonInput("");
                            setModalError(null);
                          }}
                          className={`px-2.5 py-1 rounded text-[11px] transition-colors ${
                            isSelf
                              ? "opacity-30 cursor-not-allowed bg-[#1c2d38] text-[#7c8c9a]"
                              : isDeactivated
                              ? "bg-[#00ed64]/10 hover:bg-[#00ed64]/20 text-[#00ed64] border border-[#00ed64]/30"
                              : "bg-[#fa6e39]/10 hover:bg-[#fa6e39]/20 text-[#fa6e39] border border-[#fa6e39]/30"
                          }`}
                        >
                          {isDeactivated ? "Activate" : "Deactivate"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Status Change with Mandatory Reason */}
      {statusModalUser && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-white">
              {statusModalUser.status === "ACTIVE" ? "Deactivate User Account" : "Re-activate User Account"}
            </h3>
            <p className="text-xs text-[#7c8c9a]">
              Target: <span className="text-white font-bold">{statusModalUser.name}</span> ({statusModalUser.username})
            </p>

            {modalError && (
              <div className="p-3 rounded-lg bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs">
                {modalError}
              </div>
            )}

            <div>
              <label className="block text-xs font-mono text-[#c1ccd6] mb-1.5 uppercase">
                Mandatory Governance Reason *
              </label>
              <textarea
                rows={3}
                value={reasonInput}
                onChange={(e) => setReasonInput(e.target.value)}
                placeholder="e.g. Officer transferred / Routine audit suspension / Re-verification complete..."
                className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                required
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setStatusModalUser(null)}
                className="px-4 py-2 rounded-full bg-[#1c2d38] text-[#c1ccd6] hover:text-white text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={modalSubmitting}
                onClick={handleStatusToggle}
                className="px-4 py-2 rounded-full bg-[#fa6e39] hover:bg-[#e05825] text-white font-bold text-xs disabled:opacity-60"
              >
                {modalSubmitting ? "Executing..." : "Confirm & Record Audit"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Role Modification */}
      {roleModalUser && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-white">Modify User Role</h3>
            <p className="text-xs text-[#7c8c9a]">
              Target: <span className="text-white font-bold">{roleModalUser.name}</span> (Current: {roleModalUser.role})
            </p>

            {modalError && (
              <div className="p-3 rounded-lg bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs">
                {modalError}
              </div>
            )}

            <div>
              <label className="block text-xs font-mono text-[#c1ccd6] mb-1.5 uppercase">
                New Role Assignment *
              </label>
              <select
                value={newRoleSelect}
                onChange={(e) => setNewRoleSelect(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
              >
                <option value="citizen">Citizen (Standard Landowner)</option>
                <option value="revenue_officer">Revenue Officer (Adjudicator)</option>
                <option value="administrator">Administrator (Platform Governance)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#c1ccd6] mb-1.5 uppercase">
                Mandatory Governance Reason *
              </label>
              <textarea
                rows={3}
                value={reasonInput}
                onChange={(e) => setReasonInput(e.target.value)}
                placeholder="e.g. Assigned to Tehsil Cadastral Cell under Departmental Order #412..."
                className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                required
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setRoleModalUser(null)}
                className="px-4 py-2 rounded-full bg-[#1c2d38] text-[#c1ccd6] hover:text-white text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={modalSubmitting}
                onClick={handleRoleChange}
                className="px-4 py-2 rounded-full bg-[#00ed64] hover:bg-[#00b545] text-[#001e2b] font-bold text-xs disabled:opacity-60"
              >
                {modalSubmitting ? "Updating..." : "Update Role & Audit"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Provision New User */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#00283b] border border-[#1c2d38] rounded-2xl max-w-lg w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-white">Provision New Account</h3>
            <p className="text-xs text-[#7c8c9a]">
              Every provisioned user is registered in the database with bcrypt password hashing.
            </p>

            {modalError && (
              <div className="p-3 rounded-lg bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs">
                {modalError}
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Username *</label>
                  <input
                    type="text"
                    required
                    value={newUser.username}
                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                    placeholder="e.g. ro_murthy"
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Full Name *</label>
                  <input
                    type="text"
                    required
                    value={newUser.name}
                    onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                    placeholder="e.g. S. K. Murthy"
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Email Address *</label>
                  <input
                    type="email"
                    required
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    placeholder="e.g. officer@landsync.gov.in"
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Initial Password *</label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    placeholder="Min 6 characters"
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Assigned Role *</label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  >
                    <option value="citizen">Citizen</option>
                    <option value="revenue_officer">Revenue Officer</option>
                    <option value="administrator">Administrator</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-[#c1ccd6] mb-1">Jurisdiction / Area</label>
                  <input
                    type="text"
                    value={newUser.jurisdiction}
                    onChange={(e) => setNewUser({ ...newUser, jurisdiction: e.target.value })}
                    placeholder="e.g. Model Tehsil, District"
                    className="w-full px-3 py-2 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-xs focus:outline-none focus:border-[#00ed64]"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#1c2d38]">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-full bg-[#1c2d38] text-[#c1ccd6] hover:text-white text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalSubmitting}
                  className="px-4 py-2 rounded-full bg-[#00ed64] hover:bg-[#00b545] text-[#001e2b] font-bold text-xs disabled:opacity-60"
                >
                  {modalSubmitting ? "Provisioning..." : "Provision Account"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
