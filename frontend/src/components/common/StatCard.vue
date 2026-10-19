<script setup lang="ts">
import { computed } from "vue";

type CardVariant = "default" | "primary" | "warning" | "success" | "danger";

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  badge?: string;
  icon?: string;
  variant?: CardVariant;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: "",
  badge: "",
  icon: "",
  variant: "default",
});

const valueColorClass = computed(() => {
  switch (props.variant) {
    case "primary":
      return "text-[#262626]";
    case "warning":
      return "text-[#ea580c]";
    case "success":
      return "text-[#059669]";
    case "danger":
      return "text-[#dc2626]";
    case "default":
    default:
      return "text-[#262626]";
  }
});

const badgeVariantClass = computed(() => {
  switch (props.variant) {
    case "warning":
      return "bg-[#fff7ed] text-[#c2410c] border-[#ffedd5]";
    case "success":
      return "bg-[#ecfdf5] text-[#065f46] border-[#a7f3d0]";
    case "danger":
      return "bg-[#fef2f2] text-[#b91c1c] border-[#fee2e2]";
    case "primary":
    case "default":
    default:
      return "bg-[#fafafa] text-[#515151] border-[#ededed]";
  }
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[20px] p-5 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] space-y-3 hover:border-[#17191c] transition-all duration-150 ease-out">
    <div class="flex items-center justify-between">
      <span class="text-[11px] font-medium text-[#777b86] uppercase tracking-wider">
        {{ title }}
      </span>
      <span
        v-if="badge || $slots.badge"
        class="text-[10px] font-medium tracking-wider uppercase px-2.5 py-0.5 rounded-full border"
        :class="badgeVariantClass"
      >
        <slot name="badge">{{ badge }}</slot>
      </span>
    </div>

    <div class="space-y-1">
      <div class="text-2xl sm:text-3xl font-semibold tracking-tight tabular-nums" :class="valueColorClass">
        {{ value }}
      </div>
      <p v-if="subtitle" class="text-xs text-[#777b86] font-normal">
        {{ subtitle }}
      </p>
    </div>

    <div v-if="trend" class="flex items-center space-x-1 text-xs pt-1">
      <span
        class="font-medium"
        :class="trend.isPositive ? 'text-[#065f46]' : 'text-red-600'"
      >
        {{ trend.isPositive ? '+' : '-' }}{{ trend.value }}
      </span>
      <span class="text-[#777b86]">vs periode lalu</span>
    </div>
  </div>
</template>
