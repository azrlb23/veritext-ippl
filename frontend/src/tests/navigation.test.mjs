import assert from "node:assert/strict";
import { getSegmentedNavLinks, evaluateNavigationGuard, getHomeRouteForRole } from "../utils/navigation.ts";

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

const mockRoutes = {
  landing: { path: "/", fullPath: "/", meta: {} },
  verify: { path: "/verify", fullPath: "/verify", meta: {} },
  login: { path: "/login", fullPath: "/login", meta: { guestOnly: true } },
  register: { path: "/register", fullPath: "/register", meta: { guestOnly: true } },
  onboarding: { path: "/onboarding", fullPath: "/onboarding", meta: { guestOnly: true, isStandalone: true } },
  dashboard: { path: "/dashboard", fullPath: "/dashboard", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  billing: { path: "/billing", fullPath: "/billing", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  auditDetail: { path: "/audits/test-uuid", fullPath: "/audits/test-uuid", meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"] } },
  admin: { path: "/admin", fullPath: "/admin", name: "admin", meta: { requiresAuth: true, roles: ["ADMIN"] } },
};

// 1. Navbar Navigation Links (3-Role SaaS Model)
// Guest
const guestLinks = getSegmentedNavLinks(false, "FREE");
assert.deepEqual(guestLinks.map((l) => l.name), ["Beranda", "Verifikasi QR"]);
assert.deepEqual(guestLinks.map((l) => l.to), ["/", "/verify"]);
assert.ok(!guestLinks.some((l) => ["Dashboard", "Bank Korpus", "Saldo Token", "Admin"].includes(l.name)));

// FREE & PREMIUM
for (const role of ["FREE", "PREMIUM"]) {
  const links = getSegmentedNavLinks(true, role);
  const names = links.map((l) => l.name);
  assert.deepEqual(names, ["Beranda", "Dashboard", "Saldo Token", "Verifikasi QR"]);
  assert.ok(!names.includes("Bank Korpus"));
  assert.ok(!names.includes("Admin"));
}

// ADMIN (100% Read-Only Monitoring)
const adminLinks = getSegmentedNavLinks(true, "ADMIN");
assert.deepEqual(adminLinks.map((l) => l.name), [
  "Analitik Global",
  "Kesehatan Sistem",
  "Log Transaksi",
  "Log Audit",
]);
assert.deepEqual(adminLinks.map((l) => l.to), [
  "/admin",
  "/admin#health",
  "/admin#transactions",
  "/admin#logs",
]);
const adminNames = adminLinks.map((l) => l.name);
assert.ok(!adminNames.includes("Kelola Pengguna"));
assert.ok(!adminNames.includes("Bank Korpus"));
assert.ok(!adminNames.includes("Tuning Engine AI"));
assert.ok(!adminNames.includes("Beranda"));

// 2. Navigation Guard Tests
const guestAuth = { isAuthenticated: false, role: "FREE" };
const freeAuth = { isAuthenticated: true, role: "FREE" };
const premiumAuth = { isAuthenticated: true, role: "PREMIUM" };
const adminAuth = { isAuthenticated: true, role: "ADMIN" };

// Guest access allowed
let n = mockNotif();
assert.equal(evaluateNavigationGuard(mockRoutes.landing, guestAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.verify, guestAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.login, guestAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.register, guestAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.onboarding, guestAuth, n.fn).allowed, true);

// Guest protected route redirects
for (const [key, path] of [
  ["dashboard", "/dashboard"],
  ["billing", "/billing"],
  ["auditDetail", "/audits/test-uuid"],
]) {
  n = mockNotif();
  const res = evaluateNavigationGuard(mockRoutes[key], guestAuth, n.fn);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/login", query: { redirect: path } });
}

// Guest admin route denied
n = mockNotif();
const resGuestAdmin = evaluateNavigationGuard(mockRoutes.admin, guestAuth, n.fn);
assert.equal(resGuestAdmin.allowed, false);
assert.deepEqual(resGuestAdmin.redirect, { path: "/login", query: { redirect: "/admin" } });
assert.ok(n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));

// Logged-in user guest-only redirect: FREE/PREMIUM -> /dashboard, ADMIN -> /admin
assert.deepEqual(evaluateNavigationGuard(mockRoutes.login, freeAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.register, premiumAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.onboarding, freeAuth, n.fn).redirect, { path: "/dashboard" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.login, adminAuth, n.fn).redirect, { path: "/admin" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.register, adminAuth, n.fn).redirect, { path: "/admin" });
assert.deepEqual(evaluateNavigationGuard(mockRoutes.onboarding, adminAuth, n.fn).redirect, { path: "/admin" });

// FREE and PREMIUM user allowed routes
for (const auth of [freeAuth, premiumAuth]) {
  assert.equal(evaluateNavigationGuard(mockRoutes.landing, auth, n.fn).allowed, true);
  assert.equal(evaluateNavigationGuard(mockRoutes.verify, auth, n.fn).allowed, true);
  assert.equal(evaluateNavigationGuard(mockRoutes.dashboard, auth, n.fn).allowed, true);
  assert.equal(evaluateNavigationGuard(mockRoutes.billing, auth, n.fn).allowed, true);
  assert.equal(evaluateNavigationGuard(mockRoutes.auditDetail, auth, n.fn).allowed, true);

  // Denied admin route: redirect to /dashboard
  n = mockNotif();
  const resAdmin = evaluateNavigationGuard(mockRoutes.admin, auth, n.fn);
  assert.equal(resAdmin.allowed, false);
  assert.deepEqual(resAdmin.redirect, { path: "/dashboard" });
  assert.ok(n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));
}

// ADMIN allowed routes: /admin, /, /verify
assert.equal(evaluateNavigationGuard(mockRoutes.admin, adminAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.landing, adminAuth, n.fn).allowed, true);
assert.equal(evaluateNavigationGuard(mockRoutes.verify, adminAuth, n.fn).allowed, true);

// ADMIN denied user-only routes: /dashboard, /billing, /audits/:id -> redirect to /admin
for (const [key] of [["dashboard"], ["billing"], ["auditDetail"]]) {
  n = mockNotif();
  const resAdminUserRoute = evaluateNavigationGuard(mockRoutes[key], adminAuth, n.fn);
  assert.equal(resAdminUserRoute.allowed, false);
  assert.deepEqual(resAdminUserRoute.redirect, { path: "/admin" });
  assert.ok(!n.notifs[0].msg.includes("Hanya Administrator yang diizinkan"));
}

// Edge Cases: slash route & lower-case admin
n = mockNotif();
const slashRoute = { path: "/admin/", fullPath: "/admin/", meta: { requiresAuth: true, roles: ["ADMIN"] } };
const resSlash = evaluateNavigationGuard(slashRoute, freeAuth, n.fn);
assert.equal(resSlash.allowed, false);
assert.deepEqual(resSlash.redirect, { path: "/dashboard" });
assert.ok(n.notifs[0].msg.includes("Hanya Administrator"));

const lowerAuth = { isAuthenticated: true, role: "admin" };
assert.equal(evaluateNavigationGuard(mockRoutes.admin, lowerAuth, n.fn).allowed, true);

console.log("[SUCCESS] Seluruh verifikasi navigasi 3-Role SaaS berhasil!");
