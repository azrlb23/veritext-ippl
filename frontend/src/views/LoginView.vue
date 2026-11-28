<script setup lang="ts">
import { readableDetail } from "../utils/errorMessage";
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AuthCard, LoginForm } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";
import { getHomeRouteForRole } from "../utils/navigation";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const errorMessage = ref("");
const isLoading = ref(false);
const lockoutSeconds = ref(0);

onMounted(() => {
  if (route.query.oauth_error) {
    const raw = String(route.query.oauth_error);
    try {
      errorMessage.value = decodeURIComponent(raw);
    } catch {
      errorMessage.value = raw;
    }
  }
});

function getRedirectTarget(role?: string): string {
  const userRole = role || authStore.role;
  const redirect = route.query.redirect;
  if (
    typeof redirect === "string" &&
    redirect.startsWith("/") &&
    !redirect.startsWith("//") &&
    redirect !== "/login" &&
    redirect !== "/register"
  ) {
    if (redirect === "/dashboard" && userRole === "ADMIN") {
      return "/admin";
    }
    return redirect;
  }
  return getHomeRouteForRole(userRole);
}

async function handleLogin(creds: { email: string; password: string; remember: boolean }) {
  errorMessage.value = "";
  lockoutSeconds.value = 0;
  isLoading.value = true;

  try {
    await authStore.login({
      email: creds.email,
      password: creds.password,
      remember_me: creds.remember,
    });
    router.push(getRedirectTarget(authStore.role));
  } catch (err: any) {
    if (err?.response?.status === 429) {
      lockoutSeconds.value = err.response.data?.retry_after || 60;
      errorMessage.value = "Akun terkunci sementara demi keamanan.";
    } else if (err?.response?.data) {
      errorMessage.value =
        readableDetail(err.response.data?.detail, "") ||
        err.response.data?.message ||
        "Email atau kata sandi yang Anda masukkan tidak cocok.";
    } else {
      errorMessage.value =
        err?.message || "Gagal terhubung ke server backend. Pastikan server aktif.";
    }
  } finally {
    isLoading.value = false;
  }
}

function handleOAuthGoogle() {
  showNotification("Mengarahkan ke Google...", "info");
  window.location.href = "/api/v1/auth/google/login";
}
</script>

<template>
  <AuthCard title="Masuk">
    <div class="space-y-4">
      <div class="text-[15px] font-normal text-[#4B4757] -mt-2">
        <span>Belum punya akun? </span>
        <router-link to="/register" class="inline-flex min-h-[44px] items-center font-medium text-[#0F766E] hover:underline">
          Daftar
        </router-link>
      </div>

      <LoginForm
        :loading="isLoading"
        :errorMessage="errorMessage"
        :lockoutSeconds="lockoutSeconds"
        @submit="handleLogin"
        @oauth-google="handleOAuthGoogle"
        @clear-error="errorMessage = ''"
      />
    </div>
  </AuthCard>
</template>
