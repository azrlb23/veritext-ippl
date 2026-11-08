<script setup lang="ts">
import { ref } from "vue";
import type { RegisterDTO } from "../../services/authService";
import AuthAlertBanner from "./AuthAlertBanner.vue";
import AuthField from "./AuthField.vue";
import GoogleAuthButton from "./GoogleAuthButton.vue";
import AuthSubmitButton from "./AuthSubmitButton.vue";
import RegisterPasswordFields from "./RegisterPasswordFields.vue";

withDefaults(defineProps<{ loading?: boolean; errorMessage?: string }>(), {
  loading: false,
  errorMessage: "",
});

const emit = defineEmits<{
  (e: "submit", payload: RegisterDTO): void;
  (e: "oauth-google"): void;
  (e: "clear-error"): void;
}>();

const fullName = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const agreePDP = ref(true);
const validationError = ref("");

function handleDismiss() {
  validationError.value = "";
  emit("clear-error");
}

function handleSubmit() {
  validationError.value = "";
  if (!fullName.value.trim() || !email.value.trim() || !password.value) {
    validationError.value = "Silakan lengkapi semua kolom bertanda wajib.";
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    validationError.value = "Format alamat email tidak valid (contoh: nama@email.com).";
    return;
  }
  if (password.value.length < 8) {
    validationError.value = "Kata sandi minimal 8 karakter demi keamanan akun.";
    return;
  }
  if (password.value !== confirmPassword.value) {
    validationError.value = "Konfirmasi kata sandi tidak cocok.";
    return;
  }
  if (!agreePDP.value) {
    validationError.value = "Persetujuan pemrosesan naskah wajib dicentang.";
    return;
  }

  emit("submit", {
    full_name: fullName.value.trim(),
    email: email.value.trim(),
    password: password.value,
  });
}
</script>

<template>
  <div class="w-full space-y-5">
    <AuthAlertBanner :error-message="errorMessage" :validation-error="validationError" @dismiss="handleDismiss" />

    <form class="space-y-6" @submit.prevent="handleSubmit">
      <AuthField id="reg-name" v-model="fullName" label="Nama lengkap" autocomplete="name" placeholder="Nama lengkap resmi" :disabled="loading" />
      <AuthField id="reg-email" v-model="email" label="Alamat email" type="email" autocomplete="email" placeholder="nama@email.com" :disabled="loading" />

      <RegisterPasswordFields v-model:password="password" v-model:confirm-password="confirmPassword" :disabled="loading" />

      <label class="flex min-h-[44px] w-full cursor-pointer select-none items-center space-x-2.5 text-[13.5px] leading-tight text-[#4B4757]">
        <input id="reg-pdp" v-model="agreePDP" type="checkbox" class="h-[18px] w-[18px] shrink-0 rounded accent-[#8A3FE0]" />
        <span>Saya menyetujui naskah saya diproses untuk pengujian.</span>
      </label>

      <div class="flex w-full flex-col-reverse gap-3 sm:flex-row sm:items-center">
        <GoogleAuthButton text="Daftar dengan Google" :disabled="loading" @click="emit('oauth-google')" />
        <AuthSubmitButton :loading="loading" :disabled="loading" label="Daftar" loading-label="Daftar..." />
      </div>
    </form>
  </div>
</template>
