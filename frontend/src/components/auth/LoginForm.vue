<script setup lang="ts">
import { ref } from "vue";
import Button from "../common/Button.vue";
import Alert from "../common/Alert.vue";

interface Props {
  loading?: boolean;
  errorMessage?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  errorMessage: "",
});

const emit = defineEmits<{
  (e: "submit", payload: { email: string; password: string }): void;
  (e: "clear-error"): void;
}>();

const email = ref("");
const password = ref("");
const showPassword = ref(false);
const validationError = ref("");

function handleDismiss() {
  validationError.value = "";
  emit("clear-error");
}

function handleSubmit() {
  validationError.value = "";
  if (!email.value.trim() || !password.value.trim()) {
    validationError.value = "Silakan isi email dan kata sandi Anda.";
    return;
  }
  emit("submit", {
    email: email.value.trim(),
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
        <label class="block text-xs font-bold text-audyr-ink tracking-tight">
          Alamat Email Kampus / Institusi
        </label>
        <input
          v-model="email"
          type="email"
          required
          placeholder="nama@univ.ac.id"
          class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
        />
      </div>

      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <label class="block text-xs font-bold text-audyr-ink tracking-tight">
            Kata Sandi
          </label>
          <a href="#" class="text-[11px] text-audyr-ash hover:text-audyr-ink hover:underline tracking-tight">
            Lupa kata sandi?
          </a>
        </div>
        <div class="relative">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            required
            autocomplete="current-password"
            placeholder="Kata sandi akun"
            class="w-full pl-3.5 pr-10 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-audyr-ash hover:text-audyr-ink focus:outline-none p-1 transition-colors"
            :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
          >
            <svg v-if="showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <!-- Eye Off -->
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <!-- Eye -->
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="md"
        block
        :loading="loading"
      >
        Masuk Sekarang &rarr;
      </Button>
    </form>
  </div>
</template>
