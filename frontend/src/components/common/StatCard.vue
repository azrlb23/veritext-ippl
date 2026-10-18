<script setup lang="ts">
import { computed } from "vue";

type CardVariant = "default" | "primary" | "warning" | "success" | "danger";

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  variant?: CardVariant;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: "",
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

const iconBgClass = computed(() => {
  switch (props.variant) {
    case "primary":
      return "bg-[#ededed] text-[#262626]";
    case "warning":
      return "bg-[#fff7ed] text-[#c2410c]";
    case "success":
      return "bg-[#ecfdf5] text-[#065f46]";
    case "danger":
      return "bg-[#fef2f2] text-[#b91c1c]";
    case "default":
    default:
      return "bg-[#fafafa] text-[#515151] border border-[#ededed]";
  }
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3 hover:border-[#d4d4d4] transition-colors">
    <div class="flex items-center justify-between">
      <span class="text-[11px] font-semibold text-[#515151] uppercase tracking-wider">
        {{ title }}
      </span>
      <div
        v-if="icon || $slots.icon"
        class="w-9 h-9 rounded-[4px] flex items-center justify-center font-semibold text-sm"
        :class="iconBgClass"
      >
        <slot name="icon">
          <span>{{ icon }}</span>
        </slot>
      </div>
    </div>

    <div class="space-y-1">
      <div class="text-2xl font-black font-mono tracking-tight" :class="valueColorClass">
        {{ value }}
      </div>
      <p v-if="subtitle" class="text-xs text-audyr-ash">
        {{ subtitle }}
      </p>
    </div>

    <div v-if="trend" class="flex items-center space-x-1 text-xs pt-1">
      <span
        class="font-medium"
        :class="trend.isPositive ? 'text-[#065f46]' : 'text-red-600'"
      >
        {{ trend.isPositive ? '↑' : '↓' }} {{ trend.value }}
      </span>
      <span class="text-audyr-ash">vs periode lalu</span>
    </div>
  </div>
</template>
