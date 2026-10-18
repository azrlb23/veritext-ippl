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
        icon: "✓",
        iconColor: "text-[#059669]",
      };
    case "warning":
      return {
        container: "bg-[#fff7ed] border-[#fed7aa] text-[#9a3412]",
        icon: "⚠",
        iconColor: "text-[#ea580c]",
      };
    case "error":
      return {
        container: "bg-[#fef2f2] border-[#fecaca] text-[#991b1b]",
        icon: "✕",
        iconColor: "text-[#dc2626]",
      };
    case "info":
    default:
      return {
        container: "bg-[#fafafa] border-[#ededed] text-[#262626]",
        icon: "ℹ",
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
    <div class="font-bold text-sm flex-shrink-0" :class="variantClasses.iconColor">
      <slot name="icon">{{ variantClasses.icon }}</slot>
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
