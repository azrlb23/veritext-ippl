<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";
import AuthAlertBanner from "./AuthAlertBanner.vue";
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
const showPassword = ref(false);
const validationError = ref("");
const focusedField = ref<string | null>(null);

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
  <div class="w-full space-y-4">
    <AuthAlertBanner :error-message="errorMessage" :validation-error="validationError" :is-locked-out="isLockedOut" :countdown="countdown" @dismiss="handleDismiss" />

    <form class="space-y-3.5" @submit.prevent="handleSubmit">
      <div class="w-full h-[56px] rounded-[14px] bg-[#F3F6FC] px-4 pt-1.5 pb-1 flex flex-col justify-between relative transition-colors">
        <label for="login-email" class="text-[12px] font-medium select-none" :class="focusedField === 'email' ? 'text-[#1560BD]' : 'text-[#5B6475]'">
          Alamat email
        </label>
        <input
          id="login-email"
          v-model="email"
          type="email"
          required
          autocomplete="email"
          placeholder="nama@email.com"
          :disabled="loading || isLockedOut"
          @focus="focusedField = 'email'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[15px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="focusedField === 'email' || email" class="absolute bottom-1 left-4 right-4 h-[3px] rounded-full bg-[#1A73D9]" />
      </div>

      <div class="w-full h-[56px] rounded-[14px] bg-[#F3F6FC] px-4 pt-1.5 pb-1 flex flex-col justify-between relative transition-colors">
        <div class="flex items-center justify-between">
          <label for="login-password" class="text-[12px] font-medium select-none" :class="focusedField === 'password' ? 'text-[#1560BD]' : 'text-[#5B6475]'">
            Kata sandi
          </label>
          <button type="button" @click="showPassword = !showPassword" class="text-xs text-[#5B6475] hover:text-[#0B0F19]">
            {{ showPassword ? 'Sembunyikan' : 'Lihat' }}
          </button>
        </div>
        <input
          id="login-password"
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          required
          autocomplete="current-password"
          placeholder="Masukkan kata sandi"
          :disabled="loading || isLockedOut"
          @focus="focusedField = 'password'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[15px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="focusedField === 'password' || password" class="absolute bottom-1 left-4 right-4 h-[3px] rounded-full bg-[#1A73D9]" />
      </div>

      <div class="w-full flex items-center justify-between pt-0.5 text-[14px]">
        <label class="flex items-center space-x-2 text-[#5B6475] cursor-pointer select-none">
          <input v-model="rememberMe" type="checkbox" class="w-4 h-4 rounded text-vt-primary border-vt-hair focus:ring-vt-primary" />
          <span>Ingat sesi saya</span>
        </label>
        <router-link to="/forgot-password" class="text-[#1A73D9] font-medium hover:underline">Lupa sandi?</router-link>
      </div>

      <div class="w-full flex items-center justify-between gap-3 pt-2">
        <GoogleAuthButton text="Masuk dengan Google" :disabled="loading || isLockedOut" @click="emit('oauth-google')" />
        <AuthSubmitButton :loading="loading" :disabled="loading || isLockedOut" label="Masuk" loading-label="Memverifikasi..." />
      </div>
    </form>
  </div>
</template>
