<script setup lang="ts">
import { computed } from "vue";

type BadgeVariant = "primary" | "secondary" | "success" | "warning" | "danger" | "neutral" | "info" | "mint";
type BadgeSize = "xs" | "sm" | "md";

interface Props {
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
  dotPulse?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "sm",
  dot: false,
  dotPulse: false,
});

const variantClasses = computed(() => {
  switch (props.variant) {
    case "mint":
    case "success":
      return {
        badge: "bg-[#ecfdf5] text-[#065f46] border-[#a7f3d0]",
        dot: "bg-[#059669]",
      };
    case "warning":
      return {
        badge: "bg-[#fff7ed] text-[#c2410c] border-[#ffedd5]",
        dot: "bg-[#ea580c]",
      };
    case "danger":
      return {
        badge: "bg-[#fef2f2] text-[#b91c1c] border-[#fee2e2]",
        dot: "bg-[#dc2626]",
      };
    case "info":
      return {
        badge: "bg-[#f0f9ff] text-[#0369a1] border-[#e0f2fe]",
        dot: "bg-[#0284c7]",
      };
    case "secondary":
      return {
        badge: "bg-[#171717] text-white border-[#262626]",
        dot: "bg-white",
      };
    case "neutral":
      return {
        badge: "bg-[#fafafa] text-[#515151] border-[#ededed]",
        dot: "bg-[#929292]",
      };
    case "primary":
    default:
      return {
        badge: "bg-[#ededed] text-[#262626] border-[#ededed]",
        dot: "bg-[#262626]",
      };
  }
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case "xs":
      return "text-[10px] px-2 py-0.5";
    case "md":
      return "text-xs px-3 py-1";
    case "sm":
    default:
      return "text-[11px] px-2.5 py-0.5";
  }
});
</script>

<template>
  <span
    class="inline-flex items-center font-medium tracking-tight rounded-full border transition-colors space-x-1.5"
    :class="[variantClasses.badge, sizeClasses]"
  >
    <span
      v-if="dot"
      class="w-1.5 h-1.5 rounded-full flex-shrink-0"
      :class="[variantClasses.dot, { 'animate-pulse': dotPulse }]"
    ></span>
    <span><slot /></span>
  </span>
</template>
