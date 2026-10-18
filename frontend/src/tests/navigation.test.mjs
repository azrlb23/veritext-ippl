import assert from "node:assert/strict";
import { getSegmentedNavLinks, evaluateNavigationGuard } from "../utils/navigation.ts";

console.log("[TEST] Menjalankan Pengujian Otomatis Segmentasi Hak Akses & Navigasi VeriText AI...\n");

let passedCount = 0;
function test(description, fn) {
  try {
    fn();
    console.log(`  [PASS] ${description}`);
    passedCount++;
  } catch (error) {
    console.error(`  [FAIL] FAILED: ${description}`);
    console.error(error);
    process.exit(1);
  }
}

// -------------------------------------------------------------
// Kelompok 1: Pengujian getSegmentedNavLinks (Navbar Segmentation)
// -------------------------------------------------------------
console.log("--- 1. Pengujian Segmentasi Navigasi Navbar (Desktop & Mobile) ---");

test("Kondisi 1 (Tamu / Belum Login): HANYA Beranda dan Verifikasi QR", () => {
  const links = getSegmentedNavLinks(false, "TRIAL");
  const names = links.map((l) => l.name);
  const paths = links.map((l) => l.to);

  assert.deepEqual(names, ["Beranda", "Verifikasi QR"]);
  assert.deepEqual(paths, ["/", "/verify/sample"]);

  // DILARANG menampilkan Dashboard, Bank Korpus, Saldo Token, dan Admin
  assert.ok(!names.includes("Dashboard"), "Tamu tidak boleh melihat Dashboard");
  assert.ok(!names.includes("Bank Korpus"), "Tamu tidak boleh melihat Bank Korpus");
  assert.ok(!names.includes("Saldo Token"), "Tamu tidak boleh melihat Saldo Token");
  assert.ok(!names.includes("Admin"), "Tamu tidak boleh melihat Admin");
});

test("Kondisi 2 (Mahasiswa TRIAL): Beranda, Dashboard, Saldo Token, Verifikasi QR", () => {
  const links = getSegmentedNavLinks(true, "TRIAL");
  const names = links.map((l) => l.name);

  assert.deepEqual(names, ["Beranda", "Dashboard", "Saldo Token", "Verifikasi QR"]);
  assert.ok(!names.includes("Bank Korpus"), "Mahasiswa tidak boleh melihat Bank Korpus");
  assert.ok(!names.includes("Admin"), "Mahasiswa tidak boleh melihat Admin");
});

test("Kondisi 2 (Mahasiswa PREMIUM): Beranda, Dashboard, Saldo Token, Verifikasi QR", () => {
  const links = getSegmentedNavLinks(true, "PREMIUM");
  const names = links.map((l) => l.name);

  assert.deepEqual(names, ["Beranda", "Dashboard", "Saldo Token", "Verifikasi QR"]);
  assert.ok(!names.includes("Bank Korpus"));
  assert.ok(!names.includes("Admin"));
});

test("Kondisi 2 (Mahasiswa USER): Beranda, Dashboard, Saldo Token, Verifikasi QR", () => {
  const links = getSegmentedNavLinks(true, "USER");
  const names = links.map((l) => l.name);

  assert.deepEqual(names, ["Beranda", "Dashboard", "Saldo Token", "Verifikasi QR"]);
  assert.ok(!names.includes("Bank Korpus"));
  assert.ok(!names.includes("Admin"));
});

test("Kondisi 3 (Dosen / Reviewer): Beranda, Dashboard, Bank Korpus, Saldo Token, Verifikasi QR", () => {
  const links = getSegmentedNavLinks(true, "REVIEWER");
  const names = links.map((l) => l.name);

  assert.deepEqual(names, [
    "Beranda",
    "Dashboard",
    "Bank Korpus",
    "Saldo Token",
    "Verifikasi QR",
  ]);
  assert.ok(!names.includes("Admin"), "Reviewer tidak boleh melihat Admin");
});

test("Kondisi 4 (Super Administrator): Dedicated Admin Console Links (TIDAK ADA Beranda, Saldo Token, atau Workspace Mahasiswa)", () => {
  const links = getSegmentedNavLinks(true, "ADMIN");
  const names = links.map((l) => l.name);
  const paths = links.map((l) => l.to);

  assert.deepEqual(names, [
    "Overview & Metrik",
    "Kelola Pengguna",
    "Bank Korpus",
    "Tuning Engine AI",
    "Log Audit",
  ]);
  assert.deepEqual(paths, [
    "/admin",
    "/admin#users",
    "/corpus",
    "/admin#config",
    "/admin#logs",
  ]);

  // DILARANG memuat Beranda, Saldo Token pribadi, atau Dashboard mahasiswa
  assert.ok(!names.includes("Beranda"), "Admin tidak boleh melihat Beranda publik");
  assert.ok(!names.includes("Saldo Token"), "Admin bukan pembeli kuota dan tidak boleh melihat Saldo Token pribadi");
  assert.ok(!names.includes("Dashboard"), "Admin tidak boleh melihat Workspace Mahasiswa");
});

// -------------------------------------------------------------
// Kelompok 2: Pengujian Navigation Guard (Route Protection & Roles)
// -------------------------------------------------------------
console.log("\n--- 2. Pengujian Route Navigation Guard & Role-Based Access Control ---");

function createMockNotification() {
  const notifications = [];
  return {
    notifications,
    showNotification(msg, type, title) {
      notifications.push({ msg, type, title });
    },
  };
}

// Rute-rute tiruan yang sesuai dengan definisi di router/index.ts
const mockRoutes = {
  landing: { path: "/", fullPath: "/", meta: {} },
  verify: { path: "/verify/sample", fullPath: "/verify/sample", meta: {} },
  login: { path: "/login", fullPath: "/login", meta: { guestOnly: true } },
  register: { path: "/register", fullPath: "/register", meta: { guestOnly: true } },
  dashboard: { path: "/dashboard", fullPath: "/dashboard", meta: { requiresAuth: true } },
  billing: { path: "/billing", fullPath: "/billing", meta: { requiresAuth: true } },
  auditDetail: { path: "/audits/test-uuid", fullPath: "/audits/test-uuid", meta: { requiresAuth: true } },
  corpus: {
    path: "/corpus",
    fullPath: "/corpus",
    name: "corpus",
    meta: { requiresAuth: true, roles: ["REVIEWER", "ADMIN"] },
  },
  admin: {
    path: "/admin",
    fullPath: "/admin",
    name: "admin",
    meta: { requiresAuth: true, roles: ["ADMIN"] },
  },
};

test("Tamu mengakses rute publik (/ dan /verify) diperbolehkan", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const resLanding = evaluateNavigationGuard(mockRoutes.landing, guestAuth, notif.showNotification);
  assert.equal(resLanding.allowed, true);

  const resVerify = evaluateNavigationGuard(mockRoutes.verify, guestAuth, notif.showNotification);
  assert.equal(resVerify.allowed, true);
  assert.equal(notif.notifications.length, 0);
});

test("Tamu mengakses rute guest-only (/login dan /register) diperbolehkan", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const resLogin = evaluateNavigationGuard(mockRoutes.login, guestAuth, notif.showNotification);
  assert.equal(resLogin.allowed, true);

  const resRegister = evaluateNavigationGuard(mockRoutes.register, guestAuth, notif.showNotification);
  assert.equal(resRegister.allowed, true);
});

test("Tamu mengakses rute terproteksi (/dashboard) ditolak & diarahkan ke /login?redirect=/dashboard", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.dashboard, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/dashboard" },
  });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "warning");
});

test("Tamu mengakses rute terproteksi (/billing) ditolak & diarahkan ke /login?redirect=/billing", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.billing, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/billing" },
  });
});

test("Tamu mengakses rute terproteksi (/audits/test-uuid) ditolak & diarahkan ke /login?redirect=...", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.auditDetail, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/audits/test-uuid" },
  });
});

test("Tamu mengakses rute Super Admin (/admin) ditolak & memunculkan notifikasi Super Administrator", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.admin, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/admin" },
  });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "error");
  assert.ok(
    notif.notifications[0].msg.includes("Hanya Super Administrator yang diizinkan"),
    "Pesan harus menyebutkan Super Administrator"
  );
});

test("Mahasiswa sudah login mengakses /login dialihkan otomatis ke /dashboard", () => {
  const notif = createMockNotification();
  const studentAuth = { isAuthenticated: true, role: "TRIAL" };

  const resLogin = evaluateNavigationGuard(mockRoutes.login, studentAuth, notif.showNotification);
  assert.equal(resLogin.allowed, false);
  assert.deepEqual(resLogin.redirect, { path: "/dashboard" });

  const resRegister = evaluateNavigationGuard(mockRoutes.register, studentAuth, notif.showNotification);
  assert.equal(resRegister.allowed, false);
  assert.deepEqual(resRegister.redirect, { path: "/dashboard" });
});

test("Mahasiswa sudah login mengakses /dashboard & /billing diperbolehkan", () => {
  const notif = createMockNotification();
  const studentAuth = { isAuthenticated: true, role: "TRIAL" };

  const resDash = evaluateNavigationGuard(mockRoutes.dashboard, studentAuth, notif.showNotification);
  assert.equal(resDash.allowed, true);

  const resBill = evaluateNavigationGuard(mockRoutes.billing, studentAuth, notif.showNotification);
  assert.equal(resBill.allowed, true);
});

test("Mahasiswa mengakses /corpus ditolak & dialihkan ke /dashboard dengan notifikasi Bank Korpus", () => {
  const notif = createMockNotification();
  const studentAuth = { isAuthenticated: true, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.corpus, studentAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/dashboard" });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "warning");
  assert.ok(
    notif.notifications[0].msg.includes("Hanya Dosen/Reviewer"),
    "Harus memberi peringatan hak akses Dosen/Reviewer"
  );
});

test("Mahasiswa mengakses /admin ditolak & dialihkan ke /dashboard dengan notifikasi Super Administrator", () => {
  const notif = createMockNotification();
  const studentAuth = { isAuthenticated: true, role: "PREMIUM" };

  const res = evaluateNavigationGuard(mockRoutes.admin, studentAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/dashboard" });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "error");
  assert.ok(
    notif.notifications[0].msg.includes("Hanya Super Administrator yang diizinkan"),
    "Harus menolak dengan pesan Super Administrator"
  );
});

test("Dosen / Reviewer mengakses /corpus diperbolehkan", () => {
  const notif = createMockNotification();
  const reviewerAuth = { isAuthenticated: true, role: "REVIEWER" };

  const res = evaluateNavigationGuard(mockRoutes.corpus, reviewerAuth, notif.showNotification);
  assert.equal(res.allowed, true);
  assert.equal(notif.notifications.length, 0);
});

test("Dosen / Reviewer mengakses /admin ditolak & dialihkan ke /dashboard", () => {
  const notif = createMockNotification();
  const reviewerAuth = { isAuthenticated: true, role: "REVIEWER" };

  const res = evaluateNavigationGuard(mockRoutes.admin, reviewerAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/dashboard" });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "error");
});

test("Super Admin mengakses /admin diperbolehkan", () => {
  const notif = createMockNotification();
  const adminAuth = { isAuthenticated: true, role: "ADMIN" };

  const res = evaluateNavigationGuard(mockRoutes.admin, adminAuth, notif.showNotification);
  assert.equal(res.allowed, true);
});

test("Super Admin mengakses /corpus diperbolehkan", () => {
  const notif = createMockNotification();
  const adminAuth = { isAuthenticated: true, role: "ADMIN" };

  const res = evaluateNavigationGuard(mockRoutes.corpus, adminAuth, notif.showNotification);
  assert.equal(res.allowed, true);
});

test("Super Admin mengakses /dashboard diperbolehkan", () => {
  const notif = createMockNotification();
  const adminAuth = { isAuthenticated: true, role: "ADMIN" };

  const res = evaluateNavigationGuard(mockRoutes.dashboard, adminAuth, notif.showNotification);
  assert.equal(res.allowed, true);
});

// -------------------------------------------------------------
// Kelompok 3: Pengujian Edge Cases & Keamanan Navigasi
// -------------------------------------------------------------
console.log("\n--- 3. Pengujian Edge Cases & Kekokohan Guard ---");

test("Edge Case: Trailing slash pada /admin/ oleh Mahasiswa tetap ditolak dengan notifikasi Super Administrator", () => {
  const notif = createMockNotification();
  const studentAuth = { isAuthenticated: true, role: "TRIAL" };
  const routeWithSlash = { path: "/admin/", fullPath: "/admin/", meta: { requiresAuth: true, roles: ["ADMIN"] } };

  const res = evaluateNavigationGuard(routeWithSlash, studentAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, { path: "/dashboard" });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "error");
  assert.ok(notif.notifications[0].msg.includes("Hanya Super Administrator"));
});

test("Edge Case: Role huruf kecil ('admin', 'reviewer') tetap ditangani dengan aman secara case-insensitive", () => {
  const notif = createMockNotification();
  const adminAuthLower = { isAuthenticated: true, role: "admin" };
  const reviewerAuthLower = { isAuthenticated: true, role: "reviewer" };

  const resAdmin = evaluateNavigationGuard(mockRoutes.admin, adminAuthLower, notif.showNotification);
  assert.equal(resAdmin.allowed, true);

  const resCorpus = evaluateNavigationGuard(mockRoutes.corpus, reviewerAuthLower, notif.showNotification);
  assert.equal(resCorpus.allowed, true);
});

test("Edge Case: Rute dengan batasan role tanpa flag requiresAuth eksplisit tetap menolak tamu belum login", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };
  const routeRoleOnly = { path: "/admin/sensitive", fullPath: "/admin/sensitive", meta: { roles: ["ADMIN"] } };

  const res = evaluateNavigationGuard(routeRoleOnly, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/admin/sensitive" },
  });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "error");
});

test("Edge Case: Tamu belum login mengakses /corpus ditolak & dialihkan ke /login?redirect=/corpus", () => {
  const notif = createMockNotification();
  const guestAuth = { isAuthenticated: false, role: "TRIAL" };

  const res = evaluateNavigationGuard(mockRoutes.corpus, guestAuth, notif.showNotification);
  assert.equal(res.allowed, false);
  assert.deepEqual(res.redirect, {
    path: "/login",
    query: { redirect: "/corpus" },
  });
  assert.equal(notif.notifications.length, 1);
  assert.equal(notif.notifications[0].type, "warning");
  assert.ok(notif.notifications[0].msg.includes("Silakan masuk terlebih dahulu"));
});

console.log(`\n[SUCCESS] Seluruh ${passedCount} pengujian berhasil diverifikasi tanpa kegagalan!`);
