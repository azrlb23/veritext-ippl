import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import LandingView from "../views/LandingView.vue";
import DashboardView from "../views/DashboardView.vue";
import AuditDetailView from "../views/AuditDetailView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import CorpusView from "../views/CorpusView.vue";
import BillingView from "../views/BillingView.vue";
import VerifyView from "../views/VerifyView.vue";
import AdminView from "../views/AdminView.vue";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    roles?: string[];
    title?: string;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "landing",
    component: LandingView,
    meta: {
      title: "VeriText AI - Sistem Deteksi Plagiarisme Hybrid",
    },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    meta: {
      requiresAuth: true,
      title: "Dashboard Pengujian - VeriText AI",
    },
  },
  {
    path: "/audits/:id",
    name: "audit-detail",
    component: AuditDetailView,
    meta: {
      requiresAuth: true,
      title: "Detail Laporan Audit - VeriText AI",
    },
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: {
      guestOnly: true,
      title: "Masuk Akun - VeriText AI",
    },
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
    meta: {
      guestOnly: true,
      title: "Daftar Akun Baru - VeriText AI",
    },
  },
  {
    path: "/corpus",
    name: "corpus",
    component: CorpusView,
    meta: {
      requiresAuth: true,
      roles: ["REVIEWER", "ADMIN"],
      title: "Bank Korpus Dokumen - VeriText AI",
    },
  },
  {
    path: "/billing",
    name: "billing",
    component: BillingView,
    meta: {
      requiresAuth: true,
      title: "Saldo Token & Kuota - VeriText AI",
    },
  },
  {
    path: "/verify/:uuid?",
    name: "verify",
    component: VerifyView,
    meta: {
      title: "Verifikasi Sertifikat QR - VeriText AI",
    },
  },
  {
    path: "/admin",
    name: "admin",
    component: AdminView,
    meta: {
      requiresAuth: true,
      roles: ["ADMIN"],
      title: "Panel Administrator - VeriText AI",
    },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

import { evaluateNavigationGuard } from "../utils/navigation";

export { evaluateNavigationGuard };

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const { showNotification } = useNotification();

  const decision = evaluateNavigationGuard(to, authStore, showNotification);
  if (!decision.allowed) {
    return next(decision.redirect);
  }

  // Update title jika tersedia
  if (to.meta.title && typeof to.meta.title === "string") {
    document.title = to.meta.title;
  }

  return next();
});

export default router;
