"use client";

export interface AdminUser {
  id: string;
  username: string;
  name: string;
  email: string;
  role: string;
  jurisdiction?: string;
  status?: string;
}

const TOKEN_KEY = "landsync_admin_token";
const USER_KEY = "landsync_admin_user";

export function getApiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export function getAdminToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
}

export function getAdminUser(): AdminUser | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(USER_KEY) || localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setAdminSession(token: string, user: AdminUser, persist: boolean = false): void {
  if (typeof window === "undefined") return;
  const storage = persist ? localStorage : sessionStorage;
  storage.setItem(TOKEN_KEY, token);
  storage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAdminSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function fetchAdmin(path: string, options: RequestInit = {}): Promise<Response> {
  const apiBase = getApiBase();
  const token = getAdminToken();
  const url = `${apiBase}${path}`;

  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", headers.get("Content-Type") || "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401 && typeof window !== "undefined") {
    // Session expired or invalid
    clearAdminSession();
    if (!window.location.pathname.includes("/admin/login")) {
      window.location.href = "/admin/login?expired=true";
    }
  }

  return response;
}
