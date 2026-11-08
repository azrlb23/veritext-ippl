import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { evaluateNavigationGuard } from "../utils/navigation";
import LandingView from "../views/LandingView.vue";
import DashboardView from "../views/DashboardView.vue";
import AuditDetailView from "../views/AuditDetailView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import ForgotPasswordView from "../views/ForgotPasswordView.vue";
import ResetPasswordView from "../views/ResetPasswordView.vue";
import OAuthCallbackView from "../views/OAuthCallbackView.vue";
import OnboardingView from "../views/OnboardingView.vue";
import BillingView from "../views/BillingView.vue";
import PeriksaView from "../views/PeriksaView.vue";
import VerifyView from "../views/VerifyView.vue";
import AdminView from "../views/AdminView.vue";

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
  { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], title: "Dashboard Pengujian - VeriText AI" } },
  { path: "/periksa", name: "periksa", component: PeriksaView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Periksa Naskah - VeriText AI" } },
  { path: "/audits/:id", name: "audit-detail", component: AuditDetailView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], title: "Detail Laporan Audit - VeriText AI" } },
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Masuk Akun - VeriText AI" } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Daftar Akun Baru - VeriText AI" } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Lupa Kata Sandi - VeriText AI" } },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Setel Ulang Sandi - VeriText AI" } },
  { path: "/auth/callback", name: "oauth-callback", component: OAuthCallbackView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Autentikasi Akun - VeriText AI" } },
  { path: "/onboarding", name: "onboarding", component: OnboardingView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Lengkapi Profil Akun - VeriText AI" } },
  { path: "/billing", name: "billing", component: BillingView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], title: "Saldo Token & Kuota - VeriText AI" } },
  { path: "/verify/:uuid?", name: "verify", component: VerifyView, meta: { title: "Verifikasi Sertifikat QR - VeriText AI", backdrop: "page" } },
  { path: "/admin", name: "admin", component: AdminView, meta: { requiresAuth: true, roles: ["ADMIN"], title: "Panel Administrator - VeriText AI" } },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export { evaluateNavigationGuard };

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const { showNotification } = useNotification();
  const decision = evaluateNavigationGuard(to, authStore, showNotification);
  if (!decision.allowed) {
    return next(decision.redirect);
  }
  if (to.meta.title && typeof to.meta.title === "string") {
    document.title = to.meta.title;
  }
  return next();
});

export default router;
