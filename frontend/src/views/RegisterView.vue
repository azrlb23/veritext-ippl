<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { AuthCard, RegisterForm, type RegisterDTO } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";

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
      "Pendaftaran berhasil! Akun Anda telah dibuat dan siap digunakan.",
      "success",
      "Akun Dibuat"
    );
    router.push("/dashboard");
  } catch (err: any) {
    if (err?.response) {
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
</script>

<template>
  <AuthCard
    title="Pendaftaran Akun Baru"
    subtitle="Dapatkan akses instan ke 4-Tier Hybrid Plagiarism Detection dan bonus 5 Token Audit."
  >
    <RegisterForm
      :loading="isLoading"
      :errorMessage="errorMessage"
      @submit="handleRegister"
    />

    <template #footer>
      <span>Sudah memiliki akun?</span>
      <router-link to="/login" class="text-audyr-ink font-medium hover:underline ml-1">
        Masuk di sini
      </router-link>
    </template>
  </AuthCard>
</template>
