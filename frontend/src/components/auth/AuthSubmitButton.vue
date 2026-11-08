<script setup lang="ts">
interface Props {
  loading?: boolean;
  disabled?: boolean;
  label: string;
  loadingLabel?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  loadingLabel: "Memproses...",
});
</script>

<template>
  <button
    type="submit"
    :disabled="disabled"
    class="flex-1 sm:max-w-[170px] h-12 rounded-[24px] bg-gradient-to-br from-[#0B0F19] to-[#3A3A40] hover:opacity-95 text-white text-[15px] font-semibold flex items-center justify-center shadow-[0_8px_16px_rgba(11,15,25,0.26)] transition-all active:scale-[0.99] disabled:opacity-50"
  >
    <span v-if="loading" class="flex items-center space-x-1.5">
      <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>{{ loadingLabel }}</span>
    </span>
    <span v-else>{{ label }}</span>
  </button>
</template>
