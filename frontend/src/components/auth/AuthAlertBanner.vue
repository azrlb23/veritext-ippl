<script setup lang="ts">
interface Props {
  errorMessage?: string;
  validationError?: string;
  isLockedOut?: boolean;
  countdown?: number;
}

withDefaults(defineProps<Props>(), {
  errorMessage: "",
  validationError: "",
  isLockedOut: false,
  countdown: 0,
});

const emit = defineEmits<{
  (e: "dismiss"): void;
}>();
</script>

<template>
  <div>
    <!-- Lockout Alert (429 Brute-force Prevention) -->
    <div
      v-if="isLockedOut"
      class="p-3.5 rounded-xl bg-vt-redTint border border-vt-red/20 text-vt-red text-xs space-y-1"
    >
      <div class="flex items-center space-x-1.5 font-semibold text-xs">
        <span>Akun Terkunci Sementara</span>
      </div>
      <p class="text-xs text-vt-sub">
        Terlalu banyak percobaan masuk. Coba kembali dalam
        <strong class="text-vt-red font-mono font-bold">{{ countdown }} detik</strong>.
      </p>
    </div>

    <!-- Error Alert Standard -->
    <div
      v-else-if="errorMessage || validationError"
      class="p-3 rounded-xl bg-vt-redTint border border-vt-red/20 text-vt-red text-xs flex items-start justify-between"
    >
      <span>{{ errorMessage || validationError }}</span>
      <button
        type="button"
        @click="emit('dismiss')"
        class="text-vt-red/60 hover:text-vt-red ml-2"
        aria-label="Tutup"
      >
        &times;
      </button>
    </div>
  </div>
</template>
