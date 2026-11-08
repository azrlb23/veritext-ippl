<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { AuthCard } from "../components/auth";
import { authService } from "../services/authService";
import { useNotification } from "../composables";

const route = useRoute();
const { showNotification } = useNotification();

const token = ref("");
const isCheckingToken = ref(true);
const isTokenInvalid = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
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
  <AuthCard eyebrow="KATA SANDI BARU" :title="isTokenInvalid ? 'Tautan tidak berlaku' : 'Setel ulang sandi'" :subtitle="isTokenInvalid ? 'Minta tautan baru untuk melanjutkan.' : 'Minimal 8 karakter dengan angka dan simbol.'">
    <div v-if="isCheckingToken" class="py-10 text-center space-y-2">
      <div class="w-6 h-6 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mx-auto"></div>
      <p class="text-xs text-slate-500">Memverifikasi tautan pemulihan...</p>
    </div>

    <div v-else-if="isTokenInvalid" class="space-y-4 pt-1 font-sans">
      <div class="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs">
        Tautan pemulihan tidak valid atau kedaluwarsa.
      </div>
      <router-link to="/forgot-password" class="w-full h-11 flex items-center justify-center rounded-full bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800">
        Minta Tautan Baru &rarr;
      </router-link>
    </div>

    <div v-else-if="isSuccess" class="space-y-4 pt-1 font-sans">
      <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs space-y-1">
        <p class="font-bold text-sm">Kata sandi berhasil diperbarui</p>
        <p class="text-xs text-slate-600">Silakan masuk menggunakan kata sandi baru Anda.</p>
      </div>
      <router-link to="/login" class="w-full h-11 flex items-center justify-center rounded-full bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800">
        Masuk Sekarang &rarr;
      </router-link>
    </div>

    <div v-else class="space-y-4 font-sans">
      <div v-if="errorMessage" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex justify-between">
        <span>{{ errorMessage }}</span>
        <button type="button" @click="errorMessage = ''" class="text-red-500 font-bold ml-2">&times;</button>
      </div>

      <form class="space-y-3.5" @submit.prevent="handleSubmit">
        <div class="w-full h-14 rounded-xl bg-slate-100 px-4 pt-1.5 pb-1 flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <label for="reset-pass" class="text-[11px] font-medium text-slate-500">Kata sandi baru</label>
            <button type="button" @click="showPassword = !showPassword" class="text-xs text-slate-500 hover:text-slate-900">{{ showPassword ? 'Tutup' : 'Lihat' }}</button>
          </div>
          <input id="reset-pass" v-model="newPassword" :type="showPassword ? 'text' : 'password'" required placeholder="Minimal 8 karakter" :disabled="isLoading" class="w-full bg-transparent text-sm font-medium text-slate-900 focus:outline-none" />
        </div>

        <div class="w-full h-14 rounded-xl bg-slate-100 px-4 pt-1.5 pb-1 flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <label for="reset-conf" class="text-[11px] font-medium" :class="isPasswordMismatch ? 'text-red-600' : 'text-slate-500'">Konfirmasi kata sandi</label>
            <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="text-xs text-slate-500 hover:text-slate-900">{{ showConfirmPassword ? 'Tutup' : 'Lihat' }}</button>
          </div>
          <input id="reset-conf" v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required placeholder="Ulangi kata sandi baru" :disabled="isLoading" class="w-full bg-transparent text-sm font-medium text-slate-900 focus:outline-none" />
        </div>

        <p v-if="isPasswordMismatch" class="text-[11px] text-red-600 font-medium">Konfirmasi kata sandi tidak cocok.</p>

        <button type="submit" :disabled="isLoading" class="w-full h-11 rounded-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold transition-all disabled:opacity-50">
          {{ isLoading ? 'Menyimpan...' : 'Simpan kata sandi baru' }}
        </button>
      </form>
    </div>
  </AuthCard>
</template>
