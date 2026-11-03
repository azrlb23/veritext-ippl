<script setup lang="ts">
import { ref } from "vue";
import Button from "../common/Button.vue";
import Alert from "../common/Alert.vue";
import type { RegisterDTO } from "../../services/authService";

interface Props {
  loading?: boolean;
  errorMessage?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  errorMessage: "",
});

const emit = defineEmits<{
  (e: "submit", payload: RegisterDTO): void;
  (e: "clear-error"): void;
}>();

const fullName = ref("");
const email = ref("");
const institution = ref("");
const password = ref("");
const confirmPassword = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const agreePrivacy = ref(true);
const validationError = ref("");

function handleDismiss() {
  validationError.value = "";
  emit("clear-error");
}

function handleSubmit() {
  validationError.value = "";
  if (password.value !== confirmPassword.value) {
    validationError.value = "Konfirmasi kata sandi tidak cocok.";
    return;
  }
  if (!agreePrivacy.value) {
    validationError.value = "Anda harus menyetujui ketentuan privasi data (UU PDP No. 27/2022).";
    return;
  }

  emit("submit", {
    full_name: fullName.value.trim(),
    email: email.value.trim(),
    institution: institution.value.trim() || undefined,
    password: password.value,
  });
}
</script>

<template>
  <div class="space-y-4">
    <Alert
      v-if="errorMessage || validationError"
      variant="error"
      :message="errorMessage || validationError"
      dismissible
      @dismiss="handleDismiss"
    />

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label class="block text-xs font-bold text-audyr-ink tracking-tight">Nama Lengkap & Gelar</label>
        <input
          v-model="fullName"
          type="text"
          required
          placeholder="Dr. John Doe, M.Kom"
          class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
        />
      </div>

      <div class="space-y-1">
        <label class="block text-xs font-bold text-audyr-ink tracking-tight">Email Institusi / Pribadi</label>
        <input
          v-model="email"
          type="email"
          required
          placeholder="nama@institusi.ac.id"
          class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
        />
      </div>

      <div class="space-y-1">
        <label class="block text-xs font-bold text-audyr-ink tracking-tight">Asal Universitas / Lembaga Riset</label>
        <input
          v-model="institution"
          type="text"
          placeholder="Universitas Indonesia"
          class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
        />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1">
          <label class="block text-xs font-bold text-audyr-ink tracking-tight">Kata Sandi</label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Min. 8 karakter"
              class="w-full pl-3.5 pr-10 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-audyr-ash hover:text-audyr-ink focus:outline-none p-1 transition-colors"
              :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
            >
              <svg v-if="showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </div>
        <div class="space-y-1">
          <label class="block text-xs font-bold text-audyr-ink tracking-tight">Konfirmasi Sandi</label>
          <div class="relative">
            <input
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Ulangi sandi"
              class="w-full pl-3.5 pr-10 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-audyr-ash hover:text-audyr-ink focus:outline-none p-1 transition-colors"
              :aria-label="showConfirmPassword ? 'Sembunyikan konfirmasi sandi' : 'Tampilkan konfirmasi sandi'"
            >
              <svg v-if="showConfirmPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-start space-x-2 pt-1">
        <input
          v-model="agreePrivacy"
          type="checkbox"
          id="regPrivacyConsent"
          class="mt-1 rounded-[2px] text-audyr-ink focus:ring-audyr-ink accent-[#262626]"
        />
        <label for="regPrivacyConsent" class="text-[11px] text-audyr-ash leading-tight">
          Saya menyetujui pemrosesan dokumen sesuai ketentuan <span class="italic font-bold text-audyr-ink">Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27/2022)</span> dengan hak penghapusan permanen.
        </label>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="md"
        block
        :loading="loading"
      >
        Daftar Akun Baru &rarr;
      </Button>
    </form>
  </div>
</template>
