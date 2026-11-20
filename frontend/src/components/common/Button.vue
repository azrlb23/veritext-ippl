<script setup lang="ts">
import { computed } from "vue";

type ButtonVariant = "primary" | "secondary" | "outline" | "danger" | "ghost";
type ButtonSize = "xs" | "sm" | "md" | "lg";

interface Props {
  variant?: ButtonVariant;
  size?: ButtonSize;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  loading?: boolean;
  block?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  type: "button",
  disabled: false,
  loading: false,
  block: false,
});

const emit = defineEmits<{
  (e: "click", event: MouseEvent): void;
}>();

const variantClasses = computed(() => {
  switch (props.variant) {
    case "secondary":
      return "vt-btn-light border-[#ECECEF]";
    case "outline":
      return "bg-white hover:bg-[#EBF8F6] text-[#14111C] border-[#E8ECEB] hover:border-[#0F766E] shadow-2xs active:scale-[0.98]";
    case "danger":
      return "bg-[#B91C1C] hover:bg-[#DC2626] text-white border-transparent shadow-sm active:scale-[0.98]";
    case "ghost":
      return "bg-transparent hover:bg-[#EBF8F6] text-[#5E5A6B] hover:text-[#14111C] border-transparent shadow-none active:scale-[0.98]";
    case "primary":
    default:
      return "vt-btn-dark border-transparent";
  }
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case "xs":
      return "text-xs px-3 py-1 rounded-full";
    case "sm":
      return "text-xs px-3.5 py-1.5 rounded-full";
    case "lg":
      return "text-base px-6 py-2.5 rounded-full";
    case "md":
    default:
      return "text-sm px-5 py-2 rounded-full";
  }
});

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit("click", event);
  }
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center font-semibold tracking-tight border transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-[#0F766E]/20 disabled:cursor-not-allowed disabled:opacity-50 select-none space-x-2 font-sans cursor-pointer"
    :class="[
      variantClasses,
      sizeClasses,
      block ? 'w-full' : '',
    ]"
    @click="handleClick"
  >
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    <slot name="prefix" />
    <span v-if="$slots.default"><slot /></span>
    <slot name="suffix" />
  </button>
</template>
