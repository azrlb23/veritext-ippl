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
    class="rounded-[24px] p-8 border transition-all duration-200 relative flex flex-col justify-between space-y-6"
    :class="[
      plan.popular
        ? 'bg-[#17191c] border-neutral-800 text-white shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_25px_45px_-12px_rgba(0,0,0,0.18)] hover:border-neutral-700'
        : 'bg-white border-[#ededed] text-[#17191c] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c]'
    ]"
  >
    <!-- Popular Pill Badge (Peach & Sienna in Dark Surface) -->
    <div
      v-if="plan.popular"
      class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-0.5 bg-[#fbe1d1] text-[#5d2a1a] rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm select-none"
    >
      Paling Populer &bull; Riset &amp; Tesis
    </div>

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3
          class="font-serif text-xl sm:text-2xl font-normal tracking-tight"
          :class="plan.popular ? 'text-white' : 'text-[#17191c]'"
        >
          {{ plan.name }}
        </h3>
        <span
          class="text-[10px] font-mono px-2 py-0.5 rounded-full"
          :class="plan.popular ? 'bg-neutral-800 text-[#a3a6af]' : 'bg-[#f2f2f3] text-[#777b86]'"
        >
          {{ plan.tokens }} Token
        </span>
      </div>

      <div class="flex items-baseline space-x-2">
        <span
          class="text-3xl sm:text-4xl font-bold tracking-tight tabular-nums"
          :class="plan.popular ? 'text-white' : 'text-[#17191c]'"
        >
          {{ plan.price }}
        </span>
        <span
          class="text-xs font-normal"
          :class="plan.popular ? 'text-[#a3a6af]' : 'text-[#777b86]'"
        >
          / paket sekali bayar
        </span>
      </div>

      <p
        class="text-xs leading-relaxed font-normal"
        :class="plan.popular ? 'text-[#a3a6af]' : 'text-[#777b86]'"
      >
        {{ plan.description }}
      </p>

      <!-- Value Props List -->
      <div
        class="pt-3 border-t text-[11px] space-y-1.5"
        :class="plan.popular ? 'border-neutral-800 text-[#a3a6af]' : 'border-[#ededed] text-[#777b86]'"
      >
        <div class="flex items-center space-x-2">
          <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ Math.floor(plan.tokens / 2) }}x Audit Hybrid Lengkap (Tier 1-4)</span>
        </div>
        <div class="flex items-center space-x-2">
          <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>Sertifikat Digital QR Kriptografis SHA-256</span>
        </div>
        <div class="flex items-center space-x-2">
          <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>Masa aktif token selamanya (tanpa kedaluwarsa)</span>
        </div>
      </div>
    </div>

    <!-- Pill Action Button (Strictly rounded-full) -->
    <button
      type="button"
      :disabled="loading"
      @click="emit('select', plan)"
      class="w-full py-3 px-6 rounded-full font-medium text-xs tracking-tight transition-all duration-150 ease-out active:scale-[0.98] shadow-sm flex items-center justify-center space-x-1.5"
      :class="[
        plan.popular
          ? 'bg-white hover:bg-[#f2f2f3] text-[#17191c]'
          : 'bg-[#17191c] hover:bg-[#2e3138] text-white'
      ]"
    >
      <span v-if="loading">Memproses...</span>
      <span v-else>Beli Kuota {{ plan.name }} &rarr;</span>
    </button>
  </div>
</template>
