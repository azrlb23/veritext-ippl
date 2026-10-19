<script setup lang="ts">
import Button from "../common/Button.vue";

export interface PlanItem {
  id: string;
  name: string;
  tokens: number;
  price: string;
  description: string;
  popular?: boolean;
}

interface Props {
  plan: PlanItem;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "select", plan: PlanItem): void;
}>();
</script>

<template>
  <div
    class="rounded-[24px] p-8 border transition-all relative flex flex-col justify-between space-y-6"
    :class="[
      plan.popular
        ? 'bg-[#fbe1d1] border-[#fbe1d1] text-[#5d2a1a] shadow-[0_0_0_1px_rgba(93,42,26,0.1),0_20px_25px_-5px_rgba(93,42,26,0.08)]'
        : 'bg-white border-[#ededed] text-[#17191c] shadow-[0_0_0_1px_rgba(4,23,43,0.05)] hover:border-[#17191c]'
    ]"
  >
    <!-- Steep Blush Peach / Ink Popular Pill Badge -->
    <div
      v-if="plan.popular"
      class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-0.5 bg-[#17191c] text-white rounded-full text-[10px] italic font-medium uppercase tracking-wider"
    >
      Paling Populer
    </div>

    <div class="space-y-3">
      <h3
        class="text-lg font-semibold tracking-tight"
        :class="plan.popular ? 'text-[#5d2a1a]' : 'text-[#17191c]'"
      >
        {{ plan.name }}
      </h3>
      <div class="flex items-baseline space-x-2">
        <span
          class="text-3xl sm:text-4xl font-semibold tracking-tight tabular-nums"
          :class="plan.popular ? 'text-[#5d2a1a]' : 'text-[#17191c]'"
        >
          {{ plan.price }}
        </span>
        <span
          class="text-xs font-normal"
          :class="plan.popular ? 'text-[#5d2a1a]/80' : 'text-[#777b86]'"
        >
          / {{ plan.tokens }} Token
        </span>
      </div>
      <p
        class="text-xs leading-relaxed font-normal"
        :class="plan.popular ? 'text-[#5d2a1a]/80' : 'text-[#777b86]'"
      >
        {{ plan.description }}
      </p>
    </div>

    <Button
      :variant="plan.popular ? 'primary' : 'secondary'"
      size="md"
      block
      :loading="loading"
      :class="plan.popular ? '!bg-[#17191c] hover:!bg-[#2e3138] !text-white border-transparent' : ''"
      @click="emit('select', plan)"
    >
      Beli Paket Ini &rarr;
    </Button>
  </div>
</template>
