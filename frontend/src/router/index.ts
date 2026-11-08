import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { evaluateNavigationGuard } from "../utils/navigation";
import LandingView from "../views/LandingView.vue";
import RingkasanView from "../views/RingkasanView.vue";
import AuditDetailView from "../views/AuditDetailView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import ForgotPasswordView from "../views/ForgotPasswordView.vue";
import ResetPasswordView from "../views/ResetPasswordView.vue";
import OAuthCallbackView from "../views/OAuthCallbackView.vue";
import OnboardingView from "../views/OnboardingView.vue";
import TokenView from "../views/TokenView.vue";
import PeriksaView from "../views/PeriksaView.vue";
import RiwayatView from "../views/RiwayatView.vue";
import AkunView from "../views/AkunView.vue";
import AsistenView from "../views/AsistenView.vue";
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
  { path: "/dashboard", name: "dashboard", component: RingkasanView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Ringkasan - VeriText AI" } },
  { path: "/periksa", name: "periksa", component: PeriksaView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Periksa Naskah - VeriText AI" } },
  { path: "/riwayat", name: "riwayat", component: RiwayatView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Riwayat - VeriText AI" } },
  { path: "/akun", name: "akun", component: AkunView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Akun - VeriText AI" } },
  { path: "/asisten", name: "asisten", component: AsistenView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Asisten AI - VeriText AI" } },
  { path: "/audits/:id", name: "audit-detail", component: AuditDetailView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Hasil Pemeriksaan - VeriText AI" } },
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Masuk Akun - VeriText AI" } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Daftar Akun Baru - VeriText AI" } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Lupa Kata Sandi - VeriText AI" } },
  { path: "/reset-password", name: "reset-password", component: ResetPasswordView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Setel Ulang Sandi - VeriText AI" } },
  { path: "/auth/callback", name: "oauth-callback", component: OAuthCallbackView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Autentikasi Akun - VeriText AI" } },
  { path: "/onboarding", name: "onboarding", component: OnboardingView, meta: { guestOnly: true, isStandalone: true, backdrop: "auth", title: "Lengkapi Profil Akun - VeriText AI" } },
  { path: "/billing", name: "billing", component: TokenView, meta: { requiresAuth: true, roles: ["FREE", "PREMIUM"], backdrop: "page", title: "Token - VeriText AI" } },
  { path: "/verify/:uuid?", name: "verify", component: VerifyView, meta: { title: "Verifikasi Sertifikat QR - VeriText AI", backdrop: "page" } },
  { path: "/admin", name: "admin", component: AdminView, meta: { requiresAuth: true, roles: ["ADMIN"], backdrop: "page", title: "Pemantauan - VeriText AI" } },
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
