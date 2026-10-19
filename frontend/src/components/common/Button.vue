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
      return "bg-transparent hover:bg-[#fafafb] text-[#17191c] border-[#17191c]/20 hover:border-[#17191c] shadow-none";
    case "outline":
      return "bg-white hover:bg-[#fafafb] text-[#17191c] border-[#ededed] hover:border-[#17191c] shadow-none";
    case "danger":
      return "bg-red-600 hover:bg-red-700 text-white border-transparent shadow-none";
    case "ghost":
      return "bg-transparent hover:bg-[#f2f2f3] text-[#777b86] hover:text-[#17191c] border-transparent shadow-none";
    case "primary":
    default:
      return "bg-[#17191c] hover:bg-[#2e3138] text-white border-transparent shadow-none";
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
    class="inline-flex items-center justify-center font-medium tracking-tight border transition-colors duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-[#17191c]/20 disabled:cursor-not-allowed disabled:opacity-50 select-none space-x-2"
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
