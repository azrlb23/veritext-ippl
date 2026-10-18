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
}>();

const email = ref("");
const password = ref("");
const validationError = ref("");

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
      @dismiss="validationError = ''"
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
        <input
          v-model="password"
          type="password"
          required
          placeholder="••••••••"
          class="w-full px-3.5 py-2.5 rounded-[4px] border border-[#ededed] focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink text-sm text-audyr-ink placeholder:text-audyr-fog bg-white tracking-tight"
        />
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
