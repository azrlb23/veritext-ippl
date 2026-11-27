import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { evaluateNavigationGuard } from "../utils/navigation";
import LandingView from "../views/LandingView.vue";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    roles?: string[];
    title?: string;
    isStandalone?: boolean;
    backdrop?: "home" | "page" | "auth";
  }
}

const routes: RouteRecordRaw[] = [
  { path: "/", name: "landing", component: LandingView, meta: { title: "VeriText AI - Sistem Deteksi Plagiarisme Hybrid", backdrop: "home" } },
  { path: "/dashboard", name: "dashboard", component: () => import("../views/RingkasanView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Ringkasan - VeriText AI" } },
  { path: "/periksa", name: "periksa", component: () => import("../views/PeriksaView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Periksa Naskah - VeriText AI" } },
  { path: "/riwayat", name: "riwayat", component: () => import("../views/RiwayatView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Riwayat - VeriText AI" } },
  { path: "/akun", name: "akun", component: () => import("../views/AkunView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Akun - VeriText AI" } },
  { path: "/asisten", name: "asisten", component: () => import("../views/AsistenView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Asisten AI - VeriText AI" } },
  { path: "/audits/:id", name: "audit-detail", component: () => import("../views/AuditDetailView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Hasil Pemeriksaan - VeriText AI" } },
  { path: "/login", name: "login", component: () => import("../views/LoginView.vue"), meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Masuk Akun - VeriText AI" } },
  { path: "/register", name: "register", component: () => import("../views/RegisterView.vue"), meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Daftar Akun Baru - VeriText AI" } },
  { path: "/forgot-password", name: "forgot-password", component: () => import("../views/ForgotPasswordView.vue"), meta: { isStandalone: true, backdrop: "auth", title: "Lupa Kata Sandi - VeriText AI" } },
  { path: "/reset-password", name: "reset-password", component: () => import("../views/ResetPasswordView.vue"), meta: { isStandalone: true, backdrop: "auth", title: "Setel Ulang Sandi - VeriText AI" } },
  { path: "/auth/callback", name: "oauth-callback", component: () => import("../views/OAuthCallbackView.vue"), meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Autentikasi Akun - VeriText AI" } },
  { path: "/onboarding", name: "onboarding", component: () => import("../views/OnboardingView.vue"), meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Lengkapi Profil Akun - VeriText AI" } },
  { path: "/billing", name: "billing", component: () => import("../views/TokenView.vue"), meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Token - VeriText AI" } },
  { path: "/verify/:uuid?", name: "verify", component: () => import("../views/VerifyView.vue"), meta: { title: "Verifikasi Sertifikat QR - VeriText AI", backdrop: "page" } },
  { path: "/privasi", name: "privacy", component: () => import("../views/PrivacyView.vue"), meta: { title: "Kebijakan Privasi - VeriText AI", backdrop: "page" } },
  { path: "/ketentuan", name: "terms", component: () => import("../views/TermsView.vue"), meta: { title: "Ketentuan Layanan - VeriText AI", backdrop: "page" } },
  { path: "/admin", name: "admin", component: () => import("../views/AdminOverviewView.vue"), meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Ringkasan Pemantauan - VeriText AI" } },
  { path: "/admin/pengguna", name: "admin-users", component: () => import("../views/AdminUsersView.vue"), meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Pengguna - VeriText AI" } },
  { path: "/admin/transaksi", name: "admin-transactions", component: () => import("../views/AdminTransactionsView.vue"), meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Transaksi - VeriText AI" } },
  { path: "/admin/aktivitas", name: "admin-activity", component: () => import("../views/AdminActivityView.vue"), meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Aktivitas - VeriText AI" } },
  { path: "/admin/sistem", name: "admin-system", component: () => import("../views/AdminSystemView.vue"), meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Kesehatan Sistem - VeriText AI" } },
  { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("../views/NotFoundView.vue"), meta: { title: "Halaman Tidak Ditemukan - VeriText AI", backdrop: "page" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, behavior: "smooth", top: 96 };
    return { top: 0 };
  },
});

export { evaluateNavigationGuard };

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const { showNotification } = useNotification();
  const decision = evaluateNavigationGuard(to, authStore, showNotification);
  if (!decision.allowed) return next(decision.redirect);
  if (to.meta.title && typeof to.meta.title === "string") document.title = to.meta.title;
  return next();
});

export default router;
