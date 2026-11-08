<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { AuthCard } from "../components/auth";
import AuthField from "../components/auth/AuthField.vue";
import { authService } from "../services/authService";
import { useNotification } from "../composables";

const route = useRoute();
const { showNotification } = useNotification();

const token = ref("");
const isCheckingToken = ref(true);
const isTokenInvalid = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");

onMounted(() => {
  const qToken = route.query.token;
  if (!qToken || typeof qToken !== "string") {
    isCheckingToken.value = false;
    isTokenInvalid.value = true;
    return;
  }
  token.value = qToken;
  isCheckingToken.value = false;
});

const isPasswordMismatch = computed(() => confirmPassword.value.length > 0 && newPassword.value !== confirmPassword.value);

async function handleSubmit() {
  errorMessage.value = "";
  if (newPassword.value.length < 8) {
    errorMessage.value = "Kata sandi baru minimal 8 karakter.";
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = "Konfirmasi kata sandi tidak cocok.";
    return;
  }
  isLoading.value = true;
  try {
    await authService.resetPassword(token.value, newPassword.value);
    isSuccess.value = true;
    showNotification("Kata sandi berhasil diperbarui!", "success");
  } catch (err: any) {
    if (err?.response?.status === 400) {
      errorMessage.value = err?.response?.data?.detail || "Tautan pemulihan kedaluwarsa.";
      isTokenInvalid.value = true;
    } else errorMessage.value = err?.response?.data?.detail || "Gagal memperbarui kata sandi.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard eyebrow="Kata sandi baru" :title="isTokenInvalid ? 'Tautan tidak berlaku' : 'Setel ulang sandi'" :subtitle="isTokenInvalid ? 'Minta tautan baru untuk melanjutkan.' : 'Minimal 8 karakter dengan angka dan simbol.'">
    <div v-if="isCheckingToken" class="flex items-center gap-4 py-6" role="status">
      <svg class="h-8 w-8 shrink-0 animate-spin motion-reduce:animate-none" viewBox="0 0 36 36" fill="none" aria-hidden="true">
        <circle cx="18" cy="18" r="15" stroke="#EFEAF6" stroke-width="4" />
        <path d="M18 3 a15 15 0 0 1 15 15" stroke="#8A3FE0" stroke-width="4" stroke-linecap="round" />
      </svg>
      <p class="text-[14.5px] text-[#4B4757]">Memverifikasi tautan pemulihan...</p>
    </div>

    <div v-else-if="isTokenInvalid" class="space-y-5">
      <p class="text-[14.5px] leading-[1.65] text-[#B91C1C]">Tautan pemulihan tidak valid atau sudah kedaluwarsa.</p>
      <router-link to="/forgot-password" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">Minta tautan baru</router-link>
    </div>

    <div v-else-if="isSuccess" class="space-y-5">
      <div class="rounded-[22px] bg-[#F3EEFA] p-5 text-[14.5px] leading-[1.65] text-[#4B4757]">
        <div class="text-[17px] font-semibold text-[#15803D]">Kata sandi berhasil diperbarui</div>
        <p class="mt-1.5">Silakan masuk menggunakan kata sandi baru Anda.</p>
      </div>
      <router-link to="/login" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">Masuk sekarang</router-link>
    </div>

    <form v-else class="space-y-6" @submit.prevent="handleSubmit">
      <p v-if="errorMessage" role="alert" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
        <span>{{ errorMessage }}</span>
        <button type="button" class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none transition-colors hover:bg-[#14111C]/[0.05]" aria-label="Tutup pesan" @click="errorMessage = ''">&times;</button>
      </p>
      <AuthField id="reset-pass" v-model="newPassword" label="Kata sandi baru" type="password" revealable autocomplete="new-password" placeholder="Minimal 8 karakter" :disabled="isLoading" />
      <AuthField id="reset-conf" v-model="confirmPassword" label="Konfirmasi kata sandi" type="password" revealable autocomplete="new-password" placeholder="Ulangi kata sandi baru" :disabled="isLoading" :invalid="isPasswordMismatch" />
      <p v-if="isPasswordMismatch" class="-mt-3 text-[13px] font-medium text-[#B91C1C]">Konfirmasi kata sandi tidak cocok.</p>

      <button type="submit" :disabled="isLoading" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">{{ isLoading ? 'Menyimpan...' : 'Simpan kata sandi baru' }}</button>
    </form>
  </AuthCard>
</template>
