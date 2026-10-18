<script setup lang="ts">
import { computed } from "vue";

type AlertVariant = "info" | "success" | "warning" | "error";

interface Props {
  variant?: AlertVariant;
  title?: string;
  message?: string;
  dismissible?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "info",
  title: "",
  message: "",
  dismissible: false,
});

const emit = defineEmits<{
  (e: "dismiss"): void;
}>();

const variantClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return {
        container: "bg-[#ecfdf5] border-[#a7f3d0] text-[#065f46]",
        iconColor: "text-[#059669]",
      };
    case "warning":
      return {
        container: "bg-[#fff7ed] border-[#fed7aa] text-[#9a3412]",
        iconColor: "text-[#ea580c]",
      };
    case "error":
      return {
        container: "bg-[#fef2f2] border-[#fecaca] text-[#991b1b]",
        iconColor: "text-[#dc2626]",
      };
    case "info":
    default:
      return {
        container: "bg-[#fafafa] border-[#ededed] text-[#262626]",
        iconColor: "text-[#262626]",
      };
  }
});
</script>

<template>
  <div
    class="flex items-start p-4 rounded-[8px] border text-xs leading-relaxed space-x-3 transition-colors"
    :class="variantClasses.container"
    role="alert"
  >
    <div class="flex-shrink-0 pt-0.5" :class="variantClasses.iconColor">
      <slot name="icon">
        <svg v-if="variant === 'success'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else-if="variant === 'warning'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <svg v-else-if="variant === 'error'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </slot>
    </div>

    <div class="flex-grow space-y-0.5">
      <h5 v-if="title || $slots.title" class="font-semibold text-[#262626] tracking-tight">
        <slot name="title">{{ title }}</slot>
      </h5>
      <div>
        <slot>{{ message }}</slot>
      </div>
    </div>

    <button
      v-if="dismissible"
      type="button"
      @click="emit('dismiss')"
      class="text-[#686868] hover:text-[#262626] p-0.5 rounded-[4px] hover:bg-[#ededed] transition-colors"
      aria-label="Tutup notifikasi"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
