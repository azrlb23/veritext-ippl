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

const emit = defineEmits<{ (e: "dismiss"): void }>();
</script>

<template>
  <div role="alert">
    <div v-if="isLockedOut" class="space-y-1 text-[14px] leading-[1.6]">
      <div class="font-semibold text-[#B91C1C]">Akun terkunci sementara</div>
      <p class="text-[#4B4757]">
        Terlalu banyak percobaan masuk. Coba lagi dalam
        <strong class="font-semibold tabular-nums text-[#B91C1C]">{{ countdown }} detik</strong>.
      </p>
    </div>

    <div v-else-if="errorMessage || validationError" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
      <span>{{ errorMessage || validationError }}</span>
      <button
        type="button"
        class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none text-[#B91C1C]/70 transition-colors hover:bg-[#14111C]/[0.05] hover:text-[#B91C1C]"
        aria-label="Tutup pesan"
        @click="emit('dismiss')"
      >
        &times;
      </button>
    </div>
  </div>
</template>
