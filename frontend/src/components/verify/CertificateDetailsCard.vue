<script setup lang="ts">
import { computed } from "vue";

export interface CertificateDetails {
  uuid: string;
  title: string;
  examiner: string;
  institution: string;
  auditDate: string;
  compositeScore: number;
  lexicalScore: number;
  semanticScore: number;
  styloScore: number;
}

interface Props {
  details: CertificateDetails;
}

const props = defineProps<Props>();

const safeCompositeScore = computed(() => {
  return Math.min(100, Math.max(0, props.details.compositeScore));
});

const statusLabel = computed(() => {
  const s = safeCompositeScore.value;
  if (s <= 20) return "Orisinal / Memenuhi Standar";
  if (s <= 40) return "Perlu Perhatian Ringan";
  return "Kemiripan Signifikan";
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[24px] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] space-y-6">
    <div class="flex items-center justify-between border-b border-[#ededed] pb-4">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-[#17191c]"></span>
        <h2 class="text-xs font-semibold uppercase tracking-wider text-[#17191c]">
          Ringkasan Hasil Uji Integritas Akademik
        </h2>
      </div>
      <span class="text-[11px] font-medium tracking-tight px-3 py-0.5 rounded-full bg-[#f2f2f3] text-[#17191c] border border-[#ededed]">
        Sertifikat Publik &bull; Read-Only
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
      <!-- Circular Donut Gauge (Sienna #5d2a1a & Peach #fbe1d1) -->
      <div class="flex flex-col items-center justify-center md:col-span-1 p-4 rounded-[20px] bg-[#fafafb] border border-[#ededed] select-none text-center space-y-3">
        <div class="text-[11px] font-semibold text-[#5d2a1a] tracking-tight uppercase">
          Skor Komposit
        </div>

        <div class="relative w-24 h-24 flex items-center justify-center">
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
              :stroke-dasharray="`${safeCompositeScore}, 100`"
              stroke-linecap="round"
              stroke-width="3.5"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div class="absolute flex flex-col items-center">
            <span class="text-xl font-bold tracking-tight tabular-nums text-[#17191c]">
              {{ safeCompositeScore.toFixed(1) }}%
            </span>
            <span class="text-[8px] text-[#777b86] font-medium tracking-wider uppercase">SIMILARITY</span>
          </div>
        </div>

        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
          {{ statusLabel }}
        </span>
      </div>

      <!-- Details Metadata List -->
      <div class="md:col-span-2 space-y-3 text-xs">
        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-[#777b86] font-medium tracking-tight">Judul Naskah</span>
          <span class="col-span-2 font-semibold text-[#17191c]">{{ details.title }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-[#777b86] font-medium tracking-tight">Nama Pemeriksa</span>
          <span class="col-span-2 font-medium text-[#17191c]">{{ details.examiner }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-[#777b86] font-medium tracking-tight">Institusi Afiliasi</span>
          <span class="col-span-2 text-[#777b86]">{{ details.institution }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-[#777b86] font-medium tracking-tight">Waktu Pengujian</span>
          <span class="col-span-2 text-[#777b86] tabular-nums font-mono">{{ details.auditDate }}</span>
        </div>

        <!-- Tier Breakdown Capsule Pills -->
        <div class="pt-2">
          <div class="text-[10px] font-bold text-[#777b86] uppercase tracking-wider mb-2">Rincian per Pipeline Tier:</div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="p-2.5 bg-red-50 text-red-700 border border-red-200 rounded-full font-medium">
              Tier 1: <span class="font-bold tabular-nums font-mono">{{ details.lexicalScore }}%</span>
            </div>
            <div class="p-2.5 bg-orange-50 text-orange-700 border border-orange-200 rounded-full font-medium">
              Tier 2: <span class="font-bold tabular-nums font-mono">{{ details.semanticScore }}%</span>
            </div>
            <div class="p-2.5 bg-yellow-50 text-yellow-800 border border-yellow-200 rounded-full font-medium">
              Tier 3: <span class="font-bold tabular-nums font-mono">{{ details.styloScore }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
