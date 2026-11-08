<script setup lang="ts">
import { ref } from "vue";
import type { RegisterDTO } from "../../services/authService";
import AuthAlertBanner from "./AuthAlertBanner.vue";
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
const focusedField = ref<string | null>(null);

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
  <div class="w-full space-y-3">
    <AuthAlertBanner :error-message="errorMessage" :validation-error="validationError" @dismiss="handleDismiss" />

    <form class="space-y-2.5" @submit.prevent="handleSubmit">
      <div class="w-full h-[52px] rounded-[14px] bg-[#F3F6FC] px-4 pt-1.5 pb-1 flex flex-col justify-between relative transition-all">
        <label for="reg-name" class="text-[11px] font-medium select-none" :class="focusedField === 'name' ? 'text-[#1560BD]' : 'text-[#5B6475]'">
          Nama lengkap
        </label>
        <input
          id="reg-name"
          v-model="fullName"
          type="text"
          required
          placeholder="Nama lengkap resmi"
          :disabled="loading"
          @focus="focusedField = 'name'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[14px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="focusedField === 'name' || fullName" class="absolute bottom-1 left-4 right-4 h-[2px] rounded-full bg-[#1A73D9]"></div>
      </div>

      <div class="w-full h-[52px] rounded-[14px] bg-[#F3F6FC] px-4 pt-1.5 pb-1 flex flex-col justify-between relative transition-all">
        <label for="reg-email" class="text-[11px] font-medium select-none" :class="focusedField === 'email' ? 'text-[#1560BD]' : 'text-[#5B6475]'">
          Alamat email
        </label>
        <input
          id="reg-email"
          v-model="email"
          type="email"
          required
          autocomplete="email"
          placeholder="nama@email.com"
          :disabled="loading"
          @focus="focusedField = 'email'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[14px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="focusedField === 'email' || email" class="absolute bottom-1 left-4 right-4 h-[2px] rounded-full bg-[#1A73D9]"></div>
      </div>


      <RegisterPasswordFields v-model:password="password" v-model:confirm-password="confirmPassword" :disabled="loading" />

      <div class="w-full flex items-start space-x-2 pt-1 text-[12px] leading-tight text-[#5B6475]">
        <input id="reg-pdp" v-model="agreePDP" type="checkbox" class="mt-0.5 w-4 h-4 rounded text-vt-primary border-vt-hair focus:ring-vt-primary flex-shrink-0" />
        <label for="reg-pdp" class="cursor-pointer select-none">Saya menyetujui naskah saya diproses untuk pengujian.</label>
      </div>

      <div class="w-full flex items-center justify-between gap-3 pt-1">
        <GoogleAuthButton text="Daftar dengan Google" :disabled="loading" @click="emit('oauth-google')" />
        <AuthSubmitButton :loading="loading" :disabled="loading" label="Daftar" loading-label="Daftar..." />
      </div>
    </form>
  </div>
</template>
