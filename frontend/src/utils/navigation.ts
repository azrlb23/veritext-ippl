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
 * Returns segmented navigation links based on user authentication status and role.
 *
 * Kondisi 1: Tamu (Belum Login / !isAuthenticated)
 *   - Beranda, Verifikasi QR
 * Kondisi 2: Mahasiswa Terautentikasi (TRIAL / PREMIUM / USER)
 *   - Beranda, Dashboard, Saldo Token, Verifikasi QR
 * Kondisi 3: Dosen / Reviewer (REVIEWER)
 *   - Beranda, Dashboard, Bank Korpus, Saldo Token, Verifikasi QR
 * Kondisi 4: Super Administrator (ADMIN)
 *   - Dedicated Admin Console: Overview & Metrik, Kelola Pengguna, Bank Korpus, Tuning Engine AI, Log Audit
 *   - (DILARANG menampilkan Beranda publik, Saldo Token pribadi, atau Workspace Upload Mahasiswa)
 */
export function getSegmentedNavLinks(isAuthenticated: boolean, role: string): NavLinkItem[] {
  if (!isAuthenticated) {
    return [
      { name: "Beranda", to: "/" },
      { name: "Verifikasi QR", to: "/verify/sample" },
    ];
  }

  if (role === "ADMIN") {
    return [
      { name: "Overview & Metrik", to: "/admin" },
      { name: "Kelola Pengguna", to: "/admin#users" },
      { name: "Bank Korpus", to: "/corpus" },
      { name: "Tuning Engine AI", to: "/admin#config" },
      { name: "Log Audit", to: "/admin#logs" },
    ];
  }


  if (role === "REVIEWER") {
    return [
      { name: "Beranda", to: "/" },
      { name: "Dashboard", to: "/dashboard" },
      { name: "Bank Korpus", to: "/corpus" },
      { name: "Saldo Token", to: "/billing" },
      { name: "Verifikasi QR", to: "/verify/sample" },
    ];
  }

  return [
    { name: "Beranda", to: "/" },
    { name: "Dashboard", to: "/dashboard" },
    { name: "Saldo Token", to: "/billing" },
    { name: "Verifikasi QR", to: "/verify/sample" },
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
  const isAdminRoute =
    cleanPath === "/admin" ||
    to.name === "admin" ||
    (hasRoleRestriction && to.meta.roles?.includes("ADMIN") && to.meta.roles?.length === 1);
  const isCorpusRoute =
    cleanPath === "/corpus" ||
    to.name === "corpus" ||
    (hasRoleRestriction && to.meta.roles?.includes("REVIEWER"));

  // 1. Guest-only Routes: /login dan /register (meta: { guestOnly: true })
  // Jika pengguna sudah login dan membuka /login atau /register, redirect otomatis ke /dashboard.
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { allowed: false, redirect: { path: "/dashboard" } };
  }

  // 2. Protected Authenticated Routes: meta: { requiresAuth: true } atau memiliki pembatasan role
  // Jika belum login, redirect ke /login?redirect=... dengan notifikasi peringatan.
  const needsAuth = Boolean(to.meta.requiresAuth || hasRoleRestriction);
  if (needsAuth && !authStore.isAuthenticated) {
    if (isAdminRoute) {
      showNotification(
        "Akses Ditolak: Hanya Super Administrator yang diizinkan",
        "error",
        "Akses Ditolak"
      );
    } else {
      showNotification(
        "Silakan masuk terlebih dahulu untuk mengakses halaman ini.",
        "warning",
        "Perlu Autentikasi"
      );
    }
    return {
      allowed: false,
      redirect: {
        path: "/login",
        query: { redirect: to.fullPath },
      },
    };
  }

  // 3. Role-based Protected Routes:
  // - Protected Dosen / Reviewer: /corpus (roles: ['REVIEWER', 'ADMIN'])
  // - Protected Super Admin: /admin (roles: ['ADMIN'])
  if (hasRoleRestriction && to.meta.roles) {
    const rawRole = authStore.user?.role || authStore.role || "TRIAL";
    const userRole = String(rawRole).toUpperCase();
    const isAllowed = to.meta.roles.some((r) => r.toUpperCase() === userRole);

    if (!isAllowed) {
      if (isAdminRoute) {
        showNotification(
          "Akses Ditolak: Hanya Super Administrator yang diizinkan",
          "error",
          "Akses Ditolak"
        );
      } else if (isCorpusRoute) {
        showNotification(
          "Akses Ditolak: Hanya Dosen/Reviewer dan Administrator yang dapat mengakses Bank Korpus.",
          "warning",
          "Akses Terbatas"
        );
      } else {
        showNotification(
          "Akses Ditolak: Anda tidak memiliki izin untuk mengakses halaman ini.",
          "error",
          "Akses Ditolak"
        );
      }
      return { allowed: false, redirect: { path: "/dashboard" } };
    }
  }

  return { allowed: true };
}
