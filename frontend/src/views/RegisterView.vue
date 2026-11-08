<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { AuthCard, RegisterForm, type RegisterDTO } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";
import { getHomeRouteForRole } from "../utils/navigation";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const errorMessage = ref("");
const isLoading = ref(false);

async function handleRegister(formData: RegisterDTO) {
  errorMessage.value = "";
  isLoading.value = true;

  try {
    await authStore.register(formData);
    showNotification(
      "Pendaftaran berhasil! Akun Anda aktif dengan 5 Token Uji Coba Gratis.",
      "success",
      "Akun Berhasil Dibuat"
    );
    router.push(getHomeRouteForRole(authStore.role));
  } catch (err: any) {
    if (err?.response?.data) {
      errorMessage.value =
        err.response.data?.detail ||
        err.response.data?.message ||
        "Pendaftaran gagal. Silakan periksa kembali data Anda.";
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
  <AuthCard
    eyebrow="MULAI GRATIS"
    title="Buat akun baru"
  >
    <div class="space-y-3">
      <div class="text-[15px] font-normal text-[#5B6475] -mt-2">
        <span>Sudah punya akun? </span>
        <router-link to="/login" class="text-[#1A73D9] font-medium hover:underline">
          Masuk
        </router-link>
      </div>

      <RegisterForm
        :loading="isLoading"
        :errorMessage="errorMessage"
        @submit="handleRegister"
        @oauth-google="handleOAuthGoogle"
        @clear-error="errorMessage = ''"
      />
    </div>
  </AuthCard>
</template>
