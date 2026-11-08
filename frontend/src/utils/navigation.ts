export interface NavLinkItem {
  name: string;
  to: string;
}

export interface RouteTarget {
  path: string;
  fullPath: string;
  name?: string | symbol | null;
  meta: {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    roles?: string[];
    title?: string;
    [key: string]: any;
  };
}

export interface AuthStateContext {
  isAuthenticated: boolean;
  role: string;
  user?: { role: string } | null;
}

export type NotificationDispatcher = (
  msg: string,
  type: "info" | "success" | "warning" | "error",
  title?: string
) => void;

/**
 * Returns the canonical home route according to user role.
 * ADMIN -> '/admin', FREE/PREMIUM -> '/dashboard'.
 */
export function getHomeRouteForRole(role?: string | null): string {
  const normalizedRole = String(role || "").toUpperCase();
  return normalizedRole === "ADMIN" ? "/admin" : "/dashboard";
}

/**
 * Returns segmented navigation links based on user authentication status and role.
 * Strictly enforces 3-Role SaaS Model (FREE, PREMIUM, ADMIN).
 */
export function getSegmentedNavLinks(isAuthenticated: boolean, role: string): NavLinkItem[] {
  if (!isAuthenticated) {
    return [
      { name: "Beranda", to: "/" },
      { name: "Verifikasi QR", to: "/verify" },
    ];
  }

  const normalizedRole = String(role || "").toUpperCase();
  if (normalizedRole === "ADMIN") {
    return [
      { name: "Analitik Global", to: "/admin" },
      { name: "Kesehatan Sistem", to: "/admin#health" },
      { name: "Log Transaksi", to: "/admin#transactions" },
      { name: "Log Audit", to: "/admin#logs" },
    ];
  }

  return [
    { name: "Ringkasan", to: "/dashboard" },
    { name: "Periksa naskah", to: "/periksa" },
    { name: "Token", to: "/billing" },
    { name: "Verifikasi QR", to: "/verify" },
  ];
}

/**
 * Evaluates route access based on authentication status and user roles.
 */
export function evaluateNavigationGuard(
  to: RouteTarget,
  authStore: AuthStateContext,
  showNotification: NotificationDispatcher
): { allowed: boolean; redirect?: any } {
  const cleanPath = (to.path || "/").replace(/\/+$/, "") || "/";
  const hasRoleRestriction = Array.isArray(to.meta.roles) && to.meta.roles.length > 0;
  const rawRole = authStore.user?.role || authStore.role || "FREE";
  const userRole = String(rawRole).toUpperCase();
  const isAdminRoute =
    cleanPath === "/admin" ||
    to.name === "admin" ||
    (hasRoleRestriction && to.meta.roles?.includes("ADMIN"));

  // 1. Guest-only Routes: /login, /register, /onboarding, /auth/callback
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { allowed: false, redirect: { path: getHomeRouteForRole(userRole) } };
  }

  // 2. Protected Authenticated Routes: meta: { requiresAuth: true } atau memiliki pembatasan role
  const needsAuth = Boolean(to.meta.requiresAuth || hasRoleRestriction);
  if (needsAuth && !authStore.isAuthenticated) {
    if (isAdminRoute) {
      showNotification("Akses Ditolak: Hanya Administrator yang diizinkan", "error", "Akses Ditolak");
    } else {
      showNotification("Silakan masuk terlebih dahulu untuk mengakses halaman ini.", "warning", "Perlu Autentikasi");
    }
    return {
      allowed: false,
      redirect: { path: "/login", query: { redirect: to.fullPath } },
    };
  }

  // 3. Role-based Protected Routes
  if (hasRoleRestriction && to.meta.roles) {
    const isAllowed = to.meta.roles.some((r) => r.toUpperCase() === userRole);

    if (!isAllowed) {
      if (to.meta.roles.some((r) => r.toUpperCase() === "ADMIN")) {
        showNotification("Akses Ditolak: Hanya Administrator yang diizinkan", "error", "Akses Ditolak");
      } else {
        showNotification("Akses Ditolak: Halaman ini hanya untuk pengguna reguler.", "error", "Akses Ditolak");
      }
      return { allowed: false, redirect: { path: getHomeRouteForRole(userRole) } };
    }
  }

  return { allowed: true };
}
