<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";
import AuthAlertBanner from "./AuthAlertBanner.vue";
import AuthField from "./AuthField.vue";
import GoogleAuthButton from "./GoogleAuthButton.vue";
import AuthSubmitButton from "./AuthSubmitButton.vue";

interface Props { loading?: boolean; errorMessage?: string; lockoutSeconds?: number; }
const props = withDefaults(defineProps<Props>(), { loading: false, errorMessage: "", lockoutSeconds: 0 });
const emit = defineEmits<{
  (e: "submit", payload: { email: string; password: string; remember: boolean }): void;
  (e: "oauth-google"): void;
  (e: "clear-error"): void;
}>();

const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const validationError = ref("");

const countdown = ref(props.lockoutSeconds);
let timerInterval: ReturnType<typeof setInterval> | null = null;
if (props.lockoutSeconds > 0) startCountdown(props.lockoutSeconds);

function startCountdown(sec: number) {
  countdown.value = sec;
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    if (countdown.value > 0) countdown.value--;
    else if (timerInterval) clearInterval(timerInterval);
  }, 1000);
}

onUnmounted(() => { if (timerInterval) clearInterval(timerInterval); });
const isLockedOut = computed(() => countdown.value > 0);

function handleDismiss() {
  validationError.value = "";
  emit("clear-error");
}

function handleSubmit() {
  validationError.value = "";
  if (isLockedOut.value) {
    validationError.value = `Akses masih terkunci. Silakan tunggu ${countdown.value} detik lagi.`;
    return;
  }
  if (!email.value.trim() || !password.value.trim()) {
    validationError.value = "Silakan isi alamat email dan kata sandi akun Anda.";
    return;
  }
  const cleanEmail = email.value.trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
    validationError.value = "Format email tidak valid (contoh: nama@email.com).";
    return;
  }
  emit("submit", { email: cleanEmail, password: password.value, remember: rememberMe.value });
}
</script>

<template>
  <div class="w-full space-y-5">
    <AuthAlertBanner :error-message="errorMessage" :validation-error="validationError" :is-locked-out="isLockedOut" :countdown="countdown" @dismiss="handleDismiss" />

    <form class="space-y-6" @submit.prevent="handleSubmit">
      <AuthField id="login-email" v-model="email" label="Alamat email" type="email" autocomplete="email" placeholder="nama@email.com" :disabled="loading || isLockedOut" />
      <AuthField id="login-password" v-model="password" label="Kata sandi" type="password" revealable autocomplete="current-password" placeholder="Masukkan kata sandi" :disabled="loading || isLockedOut" />

      <div class="flex w-full items-center justify-between text-[14px]">
        <label class="flex min-h-[44px] cursor-pointer select-none items-center space-x-2 text-[#4B4757]">
          <input v-model="rememberMe" type="checkbox" class="h-[18px] w-[18px] rounded accent-[#8A3FE0]" />
          <span>Ingat sesi saya</span>
        </label>
        <router-link to="/forgot-password" class="inline-flex min-h-[44px] items-center font-medium text-[#6D28D9] hover:underline">Lupa sandi?</router-link>
      </div>

      <div class="flex w-full flex-col-reverse gap-3 sm:flex-row sm:items-center">
        <GoogleAuthButton text="Masuk dengan Google" :disabled="loading || isLockedOut" @click="emit('oauth-google')" />
        <AuthSubmitButton :loading="loading" :disabled="loading || isLockedOut" label="Masuk" loading-label="Memverifikasi..." />
      </div>
    </form>
  </div>
</template>
