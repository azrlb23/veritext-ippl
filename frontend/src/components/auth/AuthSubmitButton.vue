<script setup lang="ts">
interface Props {
  loading?: boolean;
  disabled?: boolean;
  label: string;
  loadingLabel?: string;
  iconOnly?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  loadingLabel: "Memproses...",
  iconOnly: false,
});
</script>

<template>
  <button
    type="submit"
    :disabled="disabled"
    :aria-label="iconOnly ? (loading ? loadingLabel : label) : undefined"
    :title="iconOnly ? label : undefined"
    :class="
      iconOnly
        ? 'vt-btn-dark h-[52px] w-[52px] shrink-0 rounded-full flex items-center justify-center cursor-pointer disabled:cursor-not-allowed disabled:opacity-50'
        : 'vt-btn-dark flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full text-[15px] font-semibold disabled:cursor-not-allowed disabled:opacity-50 sm:flex-1 sm:max-w-[190px]'
    "
  >
    <template v-if="iconOnly">
      <svg v-if="loading" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 12h14m-6-6 6 6-6 6" />
      </svg>
    </template>
    <template v-else>
      <span v-if="loading" class="flex items-center space-x-1.5">
        <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ loadingLabel }}</span>
      </span>
      <span v-else>{{ label }}</span>
    </template>
  </button>
</template>
