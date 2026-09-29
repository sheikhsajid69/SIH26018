"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { AdminUser, clearAdminSession, fetchAdmin, getAdminToken, getAdminUser } from "./adminAuth";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const [user, setUser] = useState<AdminUser | null>(null);
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);

  const isLoginPage = pathname === "/admin/login";

  useEffect(() => {
    if (isLoginPage) {
      setAuthorized(true);
      return;
    }

    const token = getAdminToken();
    const currentUser = getAdminUser();

    if (!token) {
      router.push("/admin/login");
      return;
    }

    if (currentUser && currentUser.role !== "administrator") {
      setAuthorized(false);
      setUser(currentUser);
      return;
    }

    setUser(currentUser);
    setAuthorized(true);
  }, [pathname, isLoginPage, router]);

  const handleLogout = async () => {
    try {
      await fetchAdmin("/api/v1/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors on logout
    } finally {
      clearAdminSession();
      router.push("/admin/login");
    }
  };

  // If on login page, render child directly
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Loading state
  if (authorized === null) {
    return (
      <div className="min-h-screen bg-[#001e2b] flex items-center justify-center text-white font-mono text-sm">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
          <span>Verifying administrative authorization...</span>
        </div>
      </div>
    );
  }

  // 403 Forbidden state if authenticated user lacks administrator role
  if (!authorized) {
    return (
      <div className="min-h-screen bg-[#001e2b] flex flex-col items-center justify-center px-4 text-center">
        <div className="w-16 h-16 rounded-full bg-[#fdf2f2]/10 border border-[#fa6e39]/40 flex items-center justify-center text-3xl mb-4">
          ⛔
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight mb-2">403 — Unauthorized Access</h1>
        <p className="text-sm text-[#7c8c9a] max-w-md mb-6">
          Your current session role (<span className="text-[#00ed64] font-mono">{user?.role || "citizen/officer"}</span>) does not possess Administrator privileges. Every administrative route is protected server-side.
        </p>
        <div className="flex gap-4">
          <Link
            href="/"
            className="px-5 py-2.5 rounded-full bg-[#00ed64] text-[#001e2b] font-bold text-xs tracking-wide"
          >
            Go to Citizen & Officer Portal
          </Link>
          <button
            onClick={handleLogout}
            className="px-5 py-2.5 rounded-full bg-[#1c2d38] text-white hover:bg-[#253947] text-xs font-mono"
          >
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  const navItems = [
    { label: "Dashboard", href: "/admin/dashboard", icon: "📊" },
    { label: "User Management", href: "/admin/users", icon: "👥" },
    { label: "Revenue Officers", href: "/admin/officers", icon: "🏛️" },
    { label: "Review Cases", href: "/admin/review-cases", icon: "⚖️" },
    { label: "Audit & Governance", href: "/admin/audit", icon: "📜" },
    { label: "AI & Providers", href: "/admin/providers", icon: "🤖" },
    { label: "Security Controls", href: "/admin/security", icon: "🛡️" },
    { label: "Reports & Analytics", href: "/admin/reports", icon: "📈" },
  ];

  return (
    <div className="min-h-screen bg-[#001e2b] flex flex-col text-white selection:bg-[#00ed64] selection:text-[#001e2b]">
      {/* Top Bar */}
      <header className="h-16 border-b border-[#1c2d38] bg-[#001e2b]/95 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center space-x-3">
          <Link href="/admin/dashboard" className="flex items-center space-x-3 group">
            <div className="w-8 h-8 rounded-lg bg-[#00ed64] flex items-center justify-center font-bold text-[#001e2b] text-base shadow-sm group-hover:scale-105 transition-transform">
              🌿
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">LANDSYNC AI</span>
              <span className="ml-2 text-[10px] px-2 py-0.5 rounded bg-[#00684a] text-[#c3f0d2] font-mono tracking-wider uppercase font-semibold">
                GOVERNANCE CONSOLE
              </span>
            </div>
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          {/* Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#00283b] border border-[#1c2d38] text-xs font-mono text-[#c1ccd6]">
            <span className="w-2 h-2 rounded-full bg-[#00ed64] animate-pulse" />
            <span>GovNet Core Active</span>
          </div>

          <Link
            href="/"
            className="text-xs text-[#7c8c9a] hover:text-[#00ed64] transition-colors font-mono hidden md:inline"
          >
            ← Public Portal
          </Link>

          {/* Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              className="flex items-center gap-2 p-1.5 rounded-full hover:bg-[#1c2d38] transition-colors border border-transparent hover:border-[#3d4f5b]"
            >
              <div className="w-7 h-7 rounded-full bg-[#00684a] text-[#00ed64] flex items-center justify-center text-xs font-bold font-mono">
                AD
              </div>
              <span className="text-xs font-medium text-[#c1ccd6] pr-1 hidden sm:inline">
                {user?.name || "Administrator"}
              </span>
            </button>

            {profileOpen && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#00283b] border border-[#1c2d38] p-4 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2">
                <div className="border-b border-[#1c2d38] pb-3 mb-3">
                  <p className="text-xs font-bold text-white">{user?.name || "Administrator"}</p>
                  <p className="text-[11px] text-[#7c8c9a] font-mono truncate">{user?.email || "admin@landsync.gov.in"}</p>
                  <span className="inline-block mt-1 text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#00ed64]/10 text-[#00ed64] border border-[#00ed64]/20">
                    Role: {user?.role || "administrator"}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full py-2 px-3 rounded-lg bg-[#fdf2f2]/10 hover:bg-[#fdf2f2]/20 text-[#fa6e39] text-xs font-medium transition-colors text-left flex items-center gap-2"
                >
                  <span>🚪</span>
                  <span>Sign Out Session</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Workspace Area: Sidebar + Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r border-[#1c2d38] bg-[#001e2b] flex flex-col justify-between p-4 hidden md:flex">
          <nav className="space-y-1">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#5c6c7a] px-3 py-1 block">
              Platform Governance
            </span>
            {navItems.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-colors ${
                    active
                      ? "bg-[#00684a] text-[#00ed64] font-semibold shadow-sm"
                      : "text-[#c1ccd6] hover:bg-[#00283b] hover:text-white"
                  }`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Institutional Integrity Notice */}
          <div className="p-3 rounded-xl bg-[#00283b] border border-[#1c2d38] text-[11px] text-[#7c8c9a] font-mono leading-relaxed">
            <div className="flex items-center gap-1.5 text-[#00ed64] font-bold mb-1">
              <span>🔒</span>
              <span>WORM IMMUTABILITY</span>
            </div>
            Every administrative mutation, status change, and role assignment is permanently audited.
          </div>
        </aside>

        {/* Content Viewport */}
        <main className="flex-1 overflow-y-auto bg-[#001824] p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
