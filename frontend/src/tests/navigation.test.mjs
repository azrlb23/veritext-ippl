import assert from "node:assert/strict";
import { getSegmentedNavLinks, getAccountMenuLinks, evaluateNavigationGuard, getHomeRouteForRole } from "../utils/navigation.ts";

console.log("[TEST] Verifikasi Segmentasi Hak Akses & Navigasi 3-Role SaaS Model...");

function mockNotif() {
  const notifs = [];
  return { notifs, fn: (msg, type, title) => notifs.push({ msg, type, title }) };
}

// 0. getHomeRouteForRole unit tests
assert.equal(getHomeRouteForRole("ADMIN"), "/admin");
assert.equal(getHomeRouteForRole("admin"), "/admin");
assert.equal(getHomeRouteForRole("FREE"), "/dashboard");
assert.equal(getHomeRouteForRole("PREMIUM"), "/dashboard");
assert.equal(getHomeRouteForRole(null), "/dashboard");
assert.equal(getHomeRouteForRole(""), "/dashboard");

const adminMeta = { requiresAuth: true, roles: ["ADMIN"] };
const mockRoutes = {
  landing: { path: "/", fullPath: "/", meta: {} },
  verify: { path: "/verify", fullPath: "/verify", meta: {} },
  login: { path: "/login", fullPath: "/login", meta: { guestOnly: true } },
  register: { path: "/register", fullPath: "/register", meta: { guestOnly: true } },
  onboarding: { path: "/onboarding", fullPath: "/onboarding", meta: { guestOnly: true, isStandalone: true } },
  dashboard: { path: "/dashboard", fullPath: "/dashboard", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  billing: { path: "/billing", fullPath: "/billing", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  auditDetail: { path: "/audits/test-uuid", fullPath: "/audits/test-uuid", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  admin: { path: "/admin", fullPath: "/admin", name: "admin", meta: adminMeta },
  adminUsers: { path: "/admin/pengguna", fullPath: "/admin/pengguna", name: "admin-users", meta: adminMeta },
  adminTransactions: { path: "/admin/transaksi", fullPath: "/admin/transaksi", name: "admin-transactions", meta: adminMeta },
  adminActivity: { path: "/admin/aktivitas", fullPath: "/admin/aktivitas", name: "admin-activity", meta: adminMeta },
  adminSystem: { path: "/admin/sistem", fullPath: "/admin/sistem", name: "admin-system", meta: adminMeta },
};

// 1. Navbar Navigation Links (3-Role SaaS Model)
const guestLinks = getSegmentedNavLinks(false, "FREE");
assert.deepEqual(guestLinks.map((l) => l.name), ["Beranda", "Verifikasi QR"]);
assert.deepEqual(guestLinks.map((l) => l.to), ["/", "/verify"]);
assert.ok(!guestLinks.some((l) => ["Ringkasan", "Dashboard", "Periksa naskah", "Bank Korpus", "Saldo Token", "Token", "Admin"].includes(l.name)));

for (const role of ["FREE", "PREMIUM"]) {
  const links = getSegmentedNavLinks(true, role);
  const names = links.map((l) => l.name);
  assert.deepEqual(names, ["Ringkasan", "Periksa naskah", "Riwayat", "Asisten AI", "Token"]);
  assert.deepEqual(getAccountMenuLinks(role).map((l) => l.name), ["Akun", "Verifikasi QR"]);
  assert.ok(!names.includes("Bank Korpus") && !names.includes("Admin"));
}

// ADMIN (100% Read-Only Monitoring)
const adminLinks = getSegmentedNavLinks(true, "ADMIN");
assert.deepEqual(adminLinks.map((l) => l.name), ["Ringkasan", "Pengguna", "Transaksi", "Aktivitas", "Sistem"]);
assert.deepEqual(adminLinks.map((l) => l.to), [
  "/admin",
  "/admin/pengguna",
  "/admin/transaksi",
  "/admin/aktivitas",
  "/admin/sistem",
]);
const adminNames = adminLinks.map((l) => l.name);
for (const forbidden of ["Kelola Pengguna", "Bank Korpus", "Tuning Engine AI", "Beranda"]) {
  assert.ok(!adminNames.includes(forbidden));
}

// 2. Navigation Guard Tests
const guestAuth = { isAuthenticated: false, role: "FREE" };
const freeAuth = { isAuthenticated: true, role: "FREE" };
const premiumAuth = { isAuthenticated: true, role: "PREMIUM" };
const adminAuth = { isAuthenticated: true, role: "ADMIN" };

// Guest access allowed
let n = mockNotif();
for (const key of ["landing", "verify", "login", "register", "onboarding"]) {
  assert.equal(evaluateNavigationGuard(mockRoutes[key], guestAuth, n.fn).allowed, true);
}

// Guest protected route redirects
for (const [key, path] of [["dashboard", "/dashboard"], ["billing", "/billing"], ["auditDetail", "/audits/test-uuid"]]) {
  n = mockNotif();
  const res = evaluateNavigationGuard(mockRoutes[key], guestAuth, n.fn);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/login", query: { redirect: path } });
}

// Guest admin routes denied (/admin & /admin/pengguna)
for (const [key, path] of [["admin", "/admin"], ["adminUsers", "/admin/pengguna"]]) {
  n = mockNotif();
  const resGuestAdmin = evaluateNavigationGuard(mockRoutes[key], guestAuth, n.fn);
  assert.equal(resGuestAdmin.allowed, false);
  assert.deepEqual(resGuestAdmin.redirect, { path: "/login", query: { redirect: path } });
  assert.ok(n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));
}

// Logged-in user guest-only redirect: FREE/PREMIUM -> /dashboard, ADMIN -> /admin
assert.deepEqual(evaluateNavigationGuard(mockRoutes.login, freeAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.register, premiumAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.onboarding, freeAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.login, adminAuth, n.fn).redirect, { path: "/admin" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.register, adminAuth, n.fn).redirect, { path: "/admin" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.onboarding, adminAuth, n.fn).redirect, { path: "/admin" });

// FREE and PREMIUM user allowed & denied admin routes
for (const auth of [freeAuth, premiumAuth]) {
  for (const key of ["landing", "verify", "dashboard", "billing", "auditDetail"]) {
    assert.equal(evaluateNavigationGuard(mockRoutes[key], auth, n.fn).allowed, true);
  }
  for (const key of ["admin", "adminUsers"]) {
    n = mockNotif();
    const resAdmin = evaluateNavigationGuard(mockRoutes[key], auth, n.fn);
    assert.equal(resAdmin.allowed, false);
    assert.deepEqual(resAdmin.redirect, { path: "/dashboard" });
    assert.ok(n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));
  }
}

// ADMIN allowed routes: /admin, /admin/*, /, /verify
for (const key of ["admin", "adminUsers", "adminTransactions", "adminActivity", "adminSystem", "landing", "verify"]) {
  assert.equal(evaluateNavigationGuard(mockRoutes[key], adminAuth, n.fn).allowed, true);
}

// ADMIN denied user-only routes: /dashboard, /billing, /audits/:id -> redirect to /admin
for (const key of ["dashboard", "billing", "auditDetail"]) {
  n = mockNotif();
  const resAdminUserRoute = evaluateNavigationGuard(mockRoutes[key], adminAuth, n.fn);
  assert.equal(resAdminUserRoute.allowed, false);
  assert.deepEqual(resAdminUserRoute.redirect, { path: "/admin" });
  assert.ok(!n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));
}

// Edge Cases: slash route, sub-route without role meta, & lower-case admin
n = mockNotif();
const slashRoute = { path: "/admin/", fullPath: "/admin/", meta: adminMeta };
const resSlash = evaluateNavigationGuard(slashRoute, freeAuth, n.fn);
assert.equal(resSlash.allowed, false);
assert.deepEqual(resSlash.redirect, { path: "/dashboard" });
assert.ok(n.notifs[0].msg.includes("Hanya Administrator"));

n = mockNotif();
const subRouteGuest = evaluateNavigationGuard({ path: "/admin/pengguna", fullPath: "/admin/pengguna", meta: { requiresAuth: true } }, guestAuth, n.fn);
assert.equal(subRouteGuest.allowed, false);
assert.deepEqual(subRouteGuest.redirect, { path: "/login", query: { redirect: "/admin/pengguna" } });
assert.ok(n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));

const lowerAuth = { isAuthenticated: true, role: "admin" };
assert.equal(evaluateNavigationGuard(mockRoutes.admin, lowerAuth, n.fn).allowed, true);

console.log("[SUCCESS] Seluruh verifikasi navigasi 3-Role SaaS berhasil!");
