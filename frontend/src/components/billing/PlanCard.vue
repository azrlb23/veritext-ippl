<script setup lang="ts">
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
    class="rounded-[28px] p-7 sm:p-8 border transition-all duration-200 relative flex flex-col justify-between space-y-6 font-sans select-none"
    :class="[
      plan.popular
        ? 'bg-white border-2 border-[#1560BD] shadow-[0_12px_36px_rgba(21,96,189,0.12)] ring-1 ring-[#1560BD]/10'
        : 'bg-[#F8FAFC] border-[#E4E8F0] hover:border-[#CBD5E1] shadow-xs'
    ]"
  >
    <!-- Popular Pill Badge -->
    <div
      v-if="plan.popular"
      class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 bg-[#1560BD] text-white rounded-full text-[10.5px] font-bold uppercase tracking-wider shadow-sm select-none whitespace-nowrap"
    >
      Paling Populer
    </div>

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-xl sm:text-2xl font-bold tracking-tight text-[#0B0F19]">
          {{ plan.name }}
        </h3>
        <span
          class="text-[11px] font-mono font-semibold px-2.5 py-1 rounded-full"
          :class="plan.popular ? 'bg-[#EAF3FE] text-[#1560BD] border border-[#BFDBFE]' : 'bg-[#E2E8F0] text-[#475569]'"
        >
          {{ plan.tokens }} Token
        </span>
      </div>

      <div class="flex items-baseline space-x-2">
        <span class="text-3xl sm:text-4xl font-extrabold tracking-tight tabular-nums text-[#0B0F19]">
          {{ plan.price }}
        </span>
        <span class="text-xs font-normal text-[#5B6475]">
          / paket sekali bayar
        </span>
      </div>

      <p class="text-xs sm:text-[13px] leading-relaxed font-normal text-[#5B6475]">
        {{ plan.description }}
      </p>

      <!-- Value Props List -->
      <div class="pt-4 border-t border-[#E4E8F0] text-xs space-y-2.5 text-[#5B6475]">
        <div class="flex items-center space-x-2.5">
          <svg class="w-4 h-4 text-[#15803D] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ Math.floor(plan.tokens / 2) }}x Audit Hybrid Lengkap (Tier 1-4)</span>
        </div>
        <div class="flex items-center space-x-2.5">
          <svg class="w-4 h-4 text-[#15803D] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>Sertifikat Digital QR Kriptografis SHA-256</span>
        </div>
        <div class="flex items-center space-x-2.5">
          <svg class="w-4 h-4 text-[#15803D] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>Masa aktif token selamanya (tanpa kedaluwarsa)</span>
        </div>
      </div>
    </div>

    <!-- Pill Action Button -->
    <button
      type="button"
      :disabled="loading"
      @click="emit('select', plan)"
      class="w-full py-3 px-6 rounded-full font-semibold text-xs sm:text-[13px] tracking-tight transition-all duration-150 ease-out active:scale-[0.98] shadow-sm flex items-center justify-center space-x-1.5 cursor-pointer"
      :class="[
        plan.popular
          ? 'bg-[#1560BD] hover:bg-[#1A73D9] text-white shadow-[0_4px_14px_rgba(21,96,189,0.35)]'
          : 'bg-[#0B0F19] hover:bg-[#1E2330] text-white shadow-[0_4px_14px_rgba(11,15,25,0.18)]'
      ]"
    >
      <span v-if="loading">Memproses...</span>
      <span v-else>Beli Kuota {{ plan.name }} &rarr;</span>
    </button>
  </div>
</template>
