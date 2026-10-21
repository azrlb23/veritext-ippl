<script setup lang="ts">
import { computed } from "vue";

interface Props {
  tokenBalance: number;
  totalAudits: number;
  completedAudits: number;
  inProgressAudits: number;
}

const props = withDefaults(defineProps<Props>(), {
  tokenBalance: 0,
  totalAudits: 0,
  completedAudits: 0,
  inProgressAudits: 0,
});

defineEmits<{
  (e: "topup"): void;
}>();

const completionRate = computed(() => {
  if (props.totalAudits <= 0) return 100;
  return Math.min(100, Math.round((props.completedAudits / props.totalAudits) * 100));
});
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- ARTIFACT 1: Saldo Token Kuota -->
    <div
      class="bg-white rounded-[22px] p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out flex flex-col justify-between space-y-4"
    >
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-semibold text-[#777b86] uppercase tracking-wider">
          Saldo Token Aktif
        </span>
        <span class="text-[10px] font-medium px-2.5 py-0.5 rounded-full border border-[#ededed] bg-[#fafafb] text-[#777b86]">
          Kredit
        </span>
      </div>

      <div class="space-y-1">
        <div class="text-3xl sm:text-4xl font-bold text-[#17191c] tracking-tight tabular-nums">
          {{ tokenBalance }} <span class="text-xs font-normal text-[#777b86] font-sans">Token</span>
        </div>
        <p class="text-[11px] text-[#777b86] leading-tight">
          Cukup untuk <strong class="font-medium text-[#17191c]">{{ Math.floor(tokenBalance / 2) }}x</strong> pengujian hybrid penuh
        </p>
      </div>

      <button
        type="button"
        @click="$emit('topup')"
        class="inline-flex items-center justify-center text-xs font-medium text-[#17191c] bg-[#f2f2f3] hover:bg-[#17191c] hover:text-white border border-[#ededed] py-1.5 px-4 rounded-full transition-colors self-start active:scale-[0.98]"
      >
        + Top Up Kuota
      </button>
    </div>

    <!-- ARTIFACT 2: Total Naskah Diuji (Histogram Card) -->
    <div
      class="bg-white rounded-[22px] p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out flex justify-between gap-4"
    >
      <!-- Left Sub-Block: Metric & Mini Histogram -->
      <div class="space-y-2 flex flex-col justify-between pr-3 border-r border-[#ededed]/80 flex-1">
        <div>
          <div class="text-2xl sm:text-3xl font-bold text-[#17191c] tabular-nums tracking-tight">
            {{ totalAudits }}
          </div>
          <div class="text-[10px] text-[#777b86] font-medium leading-tight">Total Naskah</div>
        </div>

        <!-- Mini Histogram Bars -->
        <div class="flex items-end space-x-1.5 h-10 pt-1">
          <span class="w-2 bg-[#17191c]/25 rounded-t-sm h-[35%]" title="Tier 1"></span>
          <span class="w-2 bg-[#17191c]/45 rounded-t-sm h-[60%]" title="Tier 2"></span>
          <span class="w-2 bg-[#17191c]/65 rounded-t-sm h-[80%]" title="Tier 3"></span>
          <span class="w-2 bg-[#17191c]/40 rounded-t-sm h-[50%]" title="Tier 4"></span>
          <span class="w-2 bg-[#17191c] rounded-t-sm h-[100%]" title="Hybrid"></span>
        </div>
        <div class="flex items-center space-x-1.5 text-[8px] text-[#979799] uppercase font-mono">
          <span>T1</span><span>T2</span><span>T3</span><span>T4</span><span class="text-[#17191c] font-bold">HYB</span>
        </div>
      </div>

      <!-- Right Sub-Block: Pipeline Breakdown -->
      <div class="w-24 space-y-1.5 text-xs self-center">
        <div class="text-[11px] font-semibold text-[#17191c] tracking-tight">Pipeline</div>
        <div class="space-y-1 text-[10px] text-[#777b86]">
          <div class="flex items-center justify-between">
            <span>Winnowing</span>
            <span class="text-[#17191c] font-mono font-medium">50%</span>
          </div>
          <div class="flex items-center justify-between">
            <span>pgvector</span>
            <span class="text-[#17191c] font-mono font-medium">35%</span>
          </div>
          <div class="flex items-center justify-between">
            <span>Stilometri</span>
            <span class="text-[#17191c] font-mono font-medium">15%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ARTIFACT 3: Audit Selesai (Sienna/Peach Circular Donut Gauge Card) -->
    <div
      class="bg-white rounded-[22px] p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out flex items-center justify-between gap-3 select-none"
    >
      <div class="space-y-1">
        <div class="text-[11px] font-semibold text-[#5d2a1a] tracking-tight">Audit Selesai</div>
        <div class="text-2xl sm:text-3xl font-bold text-[#17191c] tabular-nums tracking-tight">
          {{ completedAudits }}
        </div>
        <div class="text-[10px] text-[#777b86] font-medium flex items-center">
          <span>Laporan &amp; Sertifikat QR</span>
        </div>
      </div>

      <!-- Circular Donut Gauge in Sienna/Peach accent -->
      <div class="relative w-16 h-16 flex items-center justify-center flex-shrink-0">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <path
            class="text-[#fbe1d1]"
            stroke-width="3.5"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            stroke="#5d2a1a"
            :stroke-dasharray="`${completionRate}, 100`"
            stroke-linecap="round"
            stroke-width="3.5"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div class="absolute flex flex-col items-center text-center">
          <span class="text-xs font-bold text-[#17191c] tabular-nums leading-none">{{ completionRate }}%</span>
          <span class="text-[8px] text-[#777b86] font-medium leading-tight">rasio</span>
        </div>
      </div>
    </div>

    <!-- ARTIFACT 4: Sedang Diproses (Sparkline Card) -->
    <div
      class="bg-white rounded-[22px] p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out flex flex-col justify-between space-y-3"
    >
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-semibold text-[#777b86] uppercase tracking-wider">
          Sedang Diproses
        </span>
        <span
          class="text-[10px] font-medium px-2 py-0.5 rounded-full border border-[#a7f3d0] bg-[#ecfdf5] text-[#065f46]"
        >
          Worker Live
        </span>
      </div>

      <div class="flex items-baseline space-x-1.5">
        <span class="text-2xl sm:text-3xl font-bold text-[#17191c] tabular-nums">
          {{ inProgressAudits }}
        </span>
        <span class="text-[10px] text-[#777b86]">Antrean aktif Celery</span>
      </div>

      <!-- Sparkline Curve with Queue indicator -->
      <div class="pt-1 border-t border-[#ededed]/60">
        <svg class="w-full h-7 overflow-visible" viewBox="0 0 100 24" fill="none">
          <line x1="0" y1="16" x2="100" y2="16" stroke="#ededed" stroke-width="1" stroke-dasharray="2,2" />
          <path
            d="M 5 18 Q 30 16, 50 10 T 80 8 T 95 4"
            stroke="#17191c"
            stroke-width="1.75"
            stroke-linecap="round"
            fill="none"
          />
          <circle cx="95" cy="4" r="2.5" fill="#17191c" />
        </svg>
        <div class="flex justify-between text-[9px] text-[#979799] mt-0.5 font-mono">
          <span>Celery</span>
          <span>Redis</span>
          <span class="px-1 bg-[#f2f2f3] rounded text-[#17191c] font-medium">HNSW</span>
        </div>
      </div>
    </div>
  </div>
</template>
