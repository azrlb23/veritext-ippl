<script setup lang="ts">
import { computed } from "vue";

interface Props {
  scoreComposite: number | null;
  scoreLexical: number | null;
  scoreSemantic: number | null;
  scoreStylometric: number | null;
}

const props = withDefaults(defineProps<Props>(), {
  scoreComposite: 0,
  scoreLexical: 0,
  scoreSemantic: 0,
  scoreStylometric: 0,
});

const safeCompositeScore = computed(() => {
  const val = props.scoreComposite ?? 0;
  return Math.min(100, Math.max(0, val));
});

const severityStatus = computed(() => {
  const s = safeCompositeScore.value;
  if (s <= 20) {
    return {
      label: "Integritas Aman (Orisinal)",
      badgeClass: "bg-[#ecfdf5] text-[#065f46] border-[#a7f3d0]",
    };
  } else if (s <= 40) {
    return {
      label: "Perlu Perhatian Ringan",
      badgeClass: "bg-[#fff7ed] text-[#c2410c] border-[#ffedd5]",
    };
  } else if (s <= 70) {
    return {
      label: "Kemiripan Signifikan",
      badgeClass: "bg-[#fef2f2] text-[#b91c1c] border-[#fee2e2]",
    };
  } else {
    return {
      label: "Plagiarisme Kritis",
      badgeClass: "bg-[#450a0a] text-white border-transparent",
    };
  }
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 sm:gap-6">
    <!-- Steep Circular Donut Gauge Card (Sienna #5d2a1a & Peach #fbe1d1) -->
    <div
      class="md:col-span-1 bg-white border border-[#ededed] rounded-[22px] p-6 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex flex-col items-center justify-center text-center space-y-4 hover:border-[#17191c] transition-all duration-200 select-none"
    >
      <div class="text-[11px] font-semibold text-[#5d2a1a] tracking-tight uppercase">
        Skor Komposit Plagiarisme
      </div>

      <!-- Circular Gauge in Sienna/Peach accent -->
      <div class="relative w-28 h-28 flex items-center justify-center">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <!-- Background track in Peach -->
          <path
            class="text-[#fbe1d1]"
            stroke-width="3.5"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <!-- Progress stroke in Sienna -->
          <path
            stroke="#5d2a1a"
            :stroke-dasharray="`${safeCompositeScore}, 100`"
            stroke-linecap="round"
            stroke-width="3.5"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>

        <div class="absolute flex flex-col items-center text-center">
          <span class="text-2xl font-bold text-[#17191c] tabular-nums leading-none tracking-tight">
            {{ safeCompositeScore.toFixed(1) }}%
          </span>
          <span class="text-[9px] text-[#777b86] font-medium tracking-wider uppercase mt-1">
            KOMPOSIT
          </span>
        </div>
      </div>

      <!-- Severity Capsule Pill Badge -->
      <div
        class="px-3 py-1 rounded-full text-[11px] font-medium border tracking-tight"
        :class="severityStatus.badgeClass"
      >
        {{ severityStatus.label }}
      </div>
    </div>

    <!-- 3 Tier Cards Breakdown -->
    <div class="md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Tier 1 Lexical Score -->
      <div
        class="bg-white border border-[#ededed] p-5 sm:p-6 rounded-[22px] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex flex-col justify-between hover:border-[#17191c] transition-all duration-200"
      >
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-semibold text-[#b91c1c] uppercase tracking-wider">
              Tier 1 &bull; Leksikal (50%)
            </span>
            <span class="text-[9px] px-2 py-0.5 rounded-full bg-red-50 text-red-700 font-mono">
              k-gram
            </span>
          </div>
          <div class="text-3xl sm:text-4xl font-bold text-[#b91c1c] tabular-nums tracking-tight">
            {{ (scoreLexical ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#777b86] mt-3 leading-relaxed font-normal">
          Algoritma Winnowing Rabin-Karp: Kecocokan string n-gram persis (<strong class="italic font-medium text-[#b91c1c]">verbatim match</strong>) terhadap korpus.
        </p>
      </div>

      <!-- Tier 2 Semantic Score -->
      <div
        class="bg-white border border-[#ededed] p-5 sm:p-6 rounded-[22px] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex flex-col justify-between hover:border-[#17191c] transition-all duration-200"
      >
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-semibold text-[#c2410c] uppercase tracking-wider">
              Tier 2 &bull; Semantik (35%)
            </span>
            <span class="text-[9px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 font-mono">
              384-d
            </span>
          </div>
          <div class="text-3xl sm:text-4xl font-bold text-[#c2410c] tabular-nums tracking-tight">
            {{ (scoreSemantic ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#777b86] mt-3 leading-relaxed font-normal">
          pgvector HNSW: Kemiripan sudut kosinus dense embedding kalimat parafrasa tingkat lanjut (&ge; 0.78).
        </p>
      </div>

      <!-- Tier 3 Stylometric Score -->
      <div
        class="bg-white border border-[#ededed] p-5 sm:p-6 rounded-[22px] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex flex-col justify-between hover:border-[#17191c] transition-all duration-200"
      >
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-semibold text-[#854d0e] uppercase tracking-wider">
              Tier 3 &bull; Pola AI (15%)
            </span>
            <span class="text-[9px] px-2 py-0.5 rounded-full bg-yellow-50 text-yellow-800 font-mono">
              Burstiness
            </span>
          </div>
          <div class="text-3xl sm:text-4xl font-bold text-[#854d0e] tabular-nums tracking-tight">
            {{ (scoreStylometric ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#777b86] mt-3 leading-relaxed font-normal">
          Metrik Stilometri: Variansi panjang kalimat (Burstiness) &amp; rasio Type-Token untuk deteksi teks sintetis.
        </p>
      </div>
    </div>
  </div>
</template>
