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
}>();

const fullName = ref("");
const email = ref("");
const institution = ref("");
const password = ref("");
const confirmPassword = ref("");
const agreePrivacy = ref(true);
const validationError = ref("");

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
      @dismiss="validationError = ''"
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
          <input
            v-model="password"
            type="password"
            required
            placeholder="Min. 8 karakter"
            class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-xs font-bold text-audyr-ink tracking-tight">Konfirmasi Sandi</label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            placeholder="Ulangi sandi"
            class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
          />
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
