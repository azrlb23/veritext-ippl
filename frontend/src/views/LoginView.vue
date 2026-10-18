<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AuthCard, LoginForm } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const errorMessage = ref("");
const isLoading = ref(false);

function getRedirectTarget(role?: string): string {
  const redirect = route.query.redirect;
  if (
    typeof redirect === "string" &&
    redirect.startsWith("/") &&
    !redirect.startsWith("//") &&
    redirect !== "/login" &&
    redirect !== "/register"
  ) {
    if (redirect === "/dashboard" && (role === "ADMIN" || authStore.role === "ADMIN")) {
      return "/admin";
    }
    return redirect;
  }
  if (role === "ADMIN" || authStore.role === "ADMIN") {
    return "/admin";
  }
  return "/dashboard";
}

async function handleLogin(creds: { email: string; password: string }) {
  errorMessage.value = "";
  isLoading.value = true;

  try {
    await authStore.login(creds);
    showNotification("Selamat datang kembali di VeriText AI!", "success");
    router.push(getRedirectTarget(authStore.role));
  } catch (err: any) {
    if (err?.response) {
      errorMessage.value =
        err.response.data?.detail ||
        err.response.data?.message ||
        "Email atau kata sandi tidak valid.";
    } else {
      errorMessage.value =
        err?.message || "Gagal terhubung ke server backend. Pastikan server aktif.";
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard
    title="Masuk ke Akun VeriText AI"
    subtitle="Masukkan kredensial akun Anda untuk mengakses sistem deteksi plagiarisme"
  >
    <LoginForm
      :loading="isLoading"
      :errorMessage="errorMessage"
      @submit="handleLogin"
    />

    <template #footer>
      <span>Belum memiliki akun?</span>
      <router-link to="/register" class="text-audyr-ink font-medium hover:underline ml-1">
        Daftar Gratis (5 Token Percobaan)
      </router-link>
    </template>
  </AuthCard>
</template>
