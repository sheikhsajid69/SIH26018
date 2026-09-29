"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { getApiBase, setAdminSession } from "../adminAuth";

export default function AdminLoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (searchParams.get("expired") === "true") {
      setSessionExpired(true);
    }
  }, [searchParams]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSessionExpired(false);

    if (!username.trim() || !password) {
      setErrorMessage("Please enter both username/email and password.");
      return;
    }

    startTransition(async () => {
      try {
        const apiBase = getApiBase();
        const res = await fetch(`${apiBase}/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: username.trim(), password }),
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          setErrorMessage(errData.detail || "Invalid credentials.");
          return;
        }

        const data = await res.json();

        // RBAC check: only administrators can access this portal
        if (data.role !== "administrator") {
          setErrorMessage("Access denied: Your account role does not have administrator privileges.");
          return;
        }

        // Store session
        setAdminSession(
          data.access_token,
          {
            id: data.user_id || "ADM-001",
            username: data.username,
            name: data.name || "Administrator",
            email: data.email || username,
            role: data.role,
          },
          false
        );

        router.push("/admin/dashboard");
      } catch {
        setErrorMessage("Unable to connect to authorization server. Please ensure backend is running.");
      }
    });
  };

  const fillDemoAdmin = () => {
    setUsername("admin");
    setPassword("Admin@LandSync2026!");
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#001e2b] flex flex-col justify-between text-white selection:bg-[#00ed64] selection:text-[#001e2b]">
      {/* Top institutional bar */}
      <header className="border-b border-[#1c2d38] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-[#00ed64] flex items-center justify-center font-bold text-[#001e2b] text-base shadow-sm">
            🌿
          </div>
          <div>
            <span className="font-bold tracking-tight text-white text-base">LANDSYNC AI</span>
            <span className="ml-2 text-xs px-2 py-0.5 rounded bg-[#00684a] text-[#c3f0d2] font-mono">
              GOVERNANCE CONSOLE
            </span>
          </div>
        </div>
        <Link
          href="/"
          className="text-xs text-[#a8b3bc] hover:text-[#00ed64] transition-colors flex items-center gap-1 font-mono"
        >
          ← Return to Citizen & Officer Portal
        </Link>
      </header>

      {/* Main Login Card */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md bg-[#00283b] border border-[#1c2d38] rounded-2xl p-8 shadow-2xl relative">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#00684a]/40 border border-[#00ed64]/30 text-[#00ed64] mb-3 text-xl">
              🛡️
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Administrator Portal</h1>
            <p className="text-xs text-[#7c8c9a] mt-1">
              Authorized personnel only. All access attempts and administrative events are cryptographically audited.
            </p>
          </div>

          {/* Session Expired Banner */}
          {sessionExpired && (
            <div className="mb-6 p-3 rounded-lg bg-[#fff8e0]/10 border border-[#fff8e0]/30 text-[#fff8e0] text-xs flex items-center gap-2">
              <span>⚠️</span>
              <span>Your administrative session has expired. Please sign in again.</span>
            </div>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <div className="mb-6 p-3 rounded-lg bg-[#fdf2f2]/10 border border-[#fa6e39]/30 text-[#fa6e39] text-xs flex items-center gap-2">
              <span>🚫</span>
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-[#c1ccd6] mb-1.5 uppercase tracking-wider font-mono">
                Admin Username or Email
              </label>
              <input
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. admin or demo.admin001@example.invalid"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-sm focus:outline-none focus:border-[#00ed64] transition-colors placeholder:text-[#5c6c7a]"
                required
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-[#c1ccd6] uppercase tracking-wider font-mono">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-[11px] text-[#00ed64] hover:underline focus:outline-none font-mono"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
              <input
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#001e2b] border border-[#1c2d38] text-white text-sm focus:outline-none focus:border-[#00ed64] transition-colors placeholder:text-[#5c6c7a]"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isPending}
              className="w-full mt-2 py-3 rounded-full bg-[#00ed64] hover:bg-[#00b545] active:bg-[#008c34] text-[#001e2b] font-bold text-sm tracking-wide transition-all shadow-lg hover:shadow-[#00ed64]/20 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-[#001e2b] border-t-transparent rounded-full animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <span>Authenticate & Access Console</span>
              )}
            </button>
          </form>

          {/* Synthetic Demo Helper (Clearly Labeled) */}
          <div className="mt-8 pt-6 border-t border-[#1c2d38] text-center">
            <span className="text-[10px] uppercase font-mono tracking-widest text-[#7c8c9a] block mb-2">
              SIH 2026 Demo Evaluator Quick Fill
            </span>
            <button
              type="button"
              onClick={fillDemoAdmin}
              className="text-xs px-3 py-1.5 rounded-full bg-[#1c2d38] hover:bg-[#253947] text-[#c1ccd6] hover:text-white transition-colors border border-[#3d4f5b]"
            >
              Fill Demo Admin Credentials (admin)
            </button>
          </div>
        </div>
      </main>

      {/* Footer Disclaimer */}
      <footer className="border-t border-[#1c2d38] px-6 py-4 text-center text-xs text-[#5c6c7a] font-mono">
        SIH26018 · Team Void · Synthetic Demonstration Governance Platform · Non-Statutory Decision Support
      </footer>
    </div>
  );
}
