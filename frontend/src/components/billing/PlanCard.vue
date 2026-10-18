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
    class="rounded-[14px] p-8 border transition-all relative flex flex-col justify-between space-y-6"
    :class="[
      plan.popular
        ? 'bg-[#171717] border-[#262626] text-white shadow-[0_1px_3px_rgba(0,0,0,0.12)]'
        : 'bg-white border-[#ededed] text-[#262626] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-[#d4d4d4]'
    ]"
  >
    <!-- Audyr Mint Whisper Popular Pill Badge -->
    <div
      v-if="plan.popular"
      class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-0.5 bg-[#ecfdf5] border border-[#a7f3d0] text-[#065f46] rounded-full text-[10px] italic font-bold uppercase tracking-wider"
    >
      Paling Populer
    </div>

    <div class="space-y-3">
      <h3
        class="text-lg font-extrabold tracking-tight"
        :class="plan.popular ? 'text-white' : 'text-[#262626]'"
      >
        {{ plan.name }}
      </h3>
      <div class="flex items-baseline space-x-2">
        <span
          class="text-3xl sm:text-4xl font-extrabold tracking-tight tabular-nums"
          :class="plan.popular ? 'text-white' : 'text-[#262626]'"
        >
          {{ plan.price }}
        </span>
        <span
          class="text-xs font-medium"
          :class="plan.popular ? 'text-[#cbcbcb]' : 'text-[#686868]'"
        >
          / {{ plan.tokens }} Token
        </span>
      </div>
      <p
        class="text-xs leading-relaxed"
        :class="plan.popular ? 'text-[#cbcbcb]' : 'text-[#686868]'"
      >
        {{ plan.description }}
      </p>
    </div>

    <Button
      :variant="plan.popular ? 'primary' : 'secondary'"
      size="md"
      block
      :loading="loading"
      :class="plan.popular ? 'bg-white hover:bg-[#fafafa] !text-[#171717] border-transparent' : ''"
      @click="emit('select', plan)"
    >
      Beli Paket Ini &rarr;
    </Button>
  </div>
</template>
