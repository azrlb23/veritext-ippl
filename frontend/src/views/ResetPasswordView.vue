<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { AuthCard } from "../components/auth";
import AuthField from "../components/auth/AuthField.vue";
import { authService } from "../services/authService";
import { useNotification } from "../composables";
import { readableDetail } from "../utils/errorMessage";

const route = useRoute();
const { showNotification } = useNotification();

const token = ref("");
const email = ref("");
const otp = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");

const isTokenMode = computed(() => token.value.length > 0);
const isPasswordMismatch = computed(
  () => confirmPassword.value.length > 0 && newPassword.value !== confirmPassword.value
);

onMounted(() => {
  let hasSensitiveQuery = false;
  if (typeof route.query.token === "string" && route.query.token.trim()) {
    token.value = route.query.token.trim();
    hasSensitiveQuery = true;
  }
  if (typeof route.query.email === "string" && route.query.email.trim()) {
    email.value = route.query.email.trim();
    hasSensitiveQuery = true;
  }
  if (typeof route.query.otp === "string" && route.query.otp.trim()) {
    otp.value = route.query.otp.trim();
    hasSensitiveQuery = true;
  }
  if (hasSensitiveQuery && typeof window !== "undefined") {
    window.history.replaceState({}, "", "/reset-password");
  }
});

async function handleSubmit() {
  errorMessage.value = "";
  if (!isTokenMode.value) {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      errorMessage.value = "Silakan masukkan alamat email yang valid.";
      return;
    }
    if (!/^\d{6}$/.test(otp.value.trim())) {
      errorMessage.value = "Kode OTP harus terdiri dari 6 digit angka.";
      return;
    }
  }
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
    const payload = isTokenMode.value
      ? { token: token.value, new_password: newPassword.value }
      : { email: email.value.trim(), otp: otp.value.trim(), new_password: newPassword.value };
    await authService.resetPassword(payload);
    isSuccess.value = true;
    showNotification("Kata sandi berhasil diperbarui!", "success");
  } catch (err: any) {
    errorMessage.value = readableDetail(
      err?.response?.data?.detail,
      isTokenMode.value ? "Tautan pemulihan tidak valid atau kedaluwarsa." : "Kode OTP tidak valid atau kedaluwarsa."
    );
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard
    title="Setel ulang sandi"
    :subtitle="isTokenMode ? 'Buat kata sandi baru minimal 8 karakter.' : 'Masukkan email, kode OTP 6-digit, dan sandi baru.'"
  >
    <div v-if="isSuccess" class="space-y-5">
      <div class="border-b border-[#E8ECEB] pb-5 text-[14.5px] leading-[1.65] text-[#4B4757]">
        <div class="text-[16px] font-semibold text-[#0F766E]">Kata sandi berhasil diperbarui</div>
        <p class="mt-1.5">Silakan masuk menggunakan kata sandi baru Anda.</p>
      </div>
      <router-link to="/login" class="vt-btn-dark inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold">
        Masuk sekarang
      </router-link>
    </div>

    <form v-else class="space-y-6" @submit.prevent="handleSubmit">
      <p v-if="errorMessage" role="alert" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
        <span>{{ errorMessage }}</span>
        <button
          type="button"
          class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none transition-colors hover:bg-[#14111C]/[0.05]"
          aria-label="Tutup pesan"
          @click="errorMessage = ''"
        >&times;</button>
      </p>

      <div v-if="!isTokenMode" class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <AuthField id="reset-email" v-model="email" label="Alamat email" type="email" autocomplete="email" placeholder="nama@email.com" :disabled="isLoading" />
        <AuthField id="reset-otp" v-model="otp" label="Kode OTP (6 digit)" type="text" autocomplete="one-time-code" placeholder="123456" :disabled="isLoading" />
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <AuthField id="reset-pass" v-model="newPassword" label="Kata sandi baru" type="password" revealable autocomplete="new-password" placeholder="Min. 8 karakter" :disabled="isLoading" />
        <AuthField id="reset-conf" v-model="confirmPassword" label="Konfirmasi sandi" type="password" revealable autocomplete="new-password" placeholder="Ulangi sandi baru" :disabled="isLoading" :invalid="isPasswordMismatch" />
      </div>
      <p v-if="isPasswordMismatch" class="-mt-3 text-[13px] font-medium text-[#B91C1C]">Konfirmasi kata sandi tidak cocok.</p>

      <button
        type="submit"
        :disabled="isLoading"
        class="vt-btn-dark inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold disabled:cursor-not-allowed disabled:opacity-50"
      >{{ isLoading ? "Menyimpan..." : "Simpan kata sandi baru" }}</button>

      <div class="text-center text-[13.5px] text-[#5E5A6B]">
        <router-link to="/forgot-password" class="font-medium text-[#0F766E] hover:underline">
          Kirim ulang kode OTP atau pulihkan via Google
        </router-link>
      </div>
    </form>
  </AuthCard>
</template>
