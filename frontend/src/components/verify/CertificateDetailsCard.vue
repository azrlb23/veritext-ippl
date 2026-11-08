<script setup lang="ts">
import { computed } from "vue";

export interface CertificateDetails {
  uuid: string;
  title: string;
  examiner: string;
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
const emit = defineEmits<{
  (e: "reset"): void;
  (e: "copyLink"): void;
}>();

const safeCompositeScore = computed(() => Math.min(100, Math.max(0, props.details.compositeScore)));
const safeOrisinalitas = computed(() => Math.max(0, Math.min(100, 100 - safeCompositeScore.value)));
const isPassed = computed(() => safeCompositeScore.value <= 20);

const statusLabel = computed(() => {
  const s = safeCompositeScore.value;
  if (s <= 20) return "Orisinalitas Baik";
  if (s <= 40) return "Perlu Tinjauan Moderat";
  return "Kemiripan Tinggi (Revisi)";
});

const ARC_SEGMENTS = [
  { x1: 46.5, y1: 98, x2: 12.8, y2: 93.5 }, { x1: 50.1, y1: 84.3, x2: 18.7, y2: 71.3 },
  { x1: 57.2, y1: 72.1, x2: 30.2, y2: 51.4 }, { x1: 67.1, y1: 62.2, x2: 46.4, y2: 35.2 },
  { x1: 79.3, y1: 55.1, x2: 66.3, y2: 23.7 }, { x1: 93, y1: 51.5, x2: 88.5, y2: 17.8 },
  { x1: 107, y1: 51.5, x2: 111.5, y2: 17.8 }, { x1: 120.7, y1: 55.1, x2: 133.7, y2: 23.7 },
  { x1: 132.9, y1: 62.2, x2: 153.6, y2: 35.2 }, { x1: 142.8, y1: 72.1, x2: 169.8, y2: 51.4 },
  { x1: 149.9, y1: 84.3, x2: 181.3, y2: 71.3 }, { x1: 153.5, y1: 98, x2: 187.2, y2: 93.5 },
];

const activeArcCount = computed(() => Math.max(1, Math.min(12, Math.round((safeOrisinalitas.value / 100) * 12))));
</script>

<template>
  <div class="bg-white rounded-[32px] sm:rounded-[40px] border border-white/80 shadow-[0_16px_48px_rgba(138,152,184,0.18)] p-6 sm:p-8 space-y-6 font-sans select-none">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E4E8F0] gap-3">
      <div>
        <h2 class="text-xs font-bold uppercase tracking-[1.2px] text-[#0B0F19]">Ringkasan Hasil Uji Orisinalitas</h2>
      </div>
      <span class="inline-flex self-start sm:self-auto text-xs font-semibold px-3 py-1 rounded-full bg-[#EAF3FE] text-[#1560BD] border border-[#BFDBFE]">
        Sertifikat Publik - Read-Only
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
      <div class="md:col-span-5 p-6 rounded-[28px] bg-[#F8FAFC] border border-[#E4E8F0] text-center space-y-4">
        <div class="text-xs font-bold text-[#1560BD] tracking-[1px] uppercase">SKOR ORISINALITAS NASKAH</div>
        <div class="relative w-36 h-24 mx-auto flex items-center justify-center">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 200 120">
            <line v-for="(seg, idx) in ARC_SEGMENTS" :key="idx" :x1="seg.x1" :y1="seg.y1" :x2="seg.x2" :y2="seg.y2"
              :stroke="idx < activeArcCount ? (isPassed ? '#1A73D9' : '#C2410C') : '#DCE3F0'"
              :stroke-opacity="idx < activeArcCount ? (idx > 7 ? 0.7 - (idx - 8) * 0.15 : 1) : 1"
              stroke-width="7" stroke-linecap="round" />
            <text x="100" y="86" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="14" font-weight="700" :fill="isPassed ? '#15803D' : '#C2410C'">
              {{ isPassed ? 'Lolos' : 'Tinjau' }}
            </text>
            <text x="100" y="102" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="500" fill="#5B6475">
              {{ isPassed ? 'Aman' : 'Tinggi' }}
            </text>
          </svg>
        </div>
        <div class="space-y-1">
          <div class="text-3xl font-extrabold text-[#0B0F19] tracking-tight tabular-nums">{{ safeOrisinalitas.toFixed(1).replace('.', ',') }}%</div>
          <p class="text-[11px] text-[#5B6475]">Kemiripan komposit: {{ safeCompositeScore.toFixed(1) }}%</p>
        </div>
        <div class="inline-flex items-center space-x-1 px-3.5 py-1 rounded-full text-xs font-bold border"
          :class="isPassed ? 'bg-[#EAF7EE] text-[#15803D] border-[#A7F3D0]' : 'bg-[#FFF1E6] text-[#C2410C] border-[#FED7AA]'">
          <span>{{ statusLabel }}</span>
        </div>
      </div>

      <div class="md:col-span-7 space-y-3 text-xs sm:text-[13px]">
        <div class="grid grid-cols-3 border-b border-[#E4E8F0] pb-2.5">
          <span class="text-[#5B6475] font-medium">Judul Naskah</span>
          <span class="col-span-2 font-bold text-[#0B0F19] leading-snug">{{ details.title }}</span>
        </div>
        <div class="grid grid-cols-3 border-b border-[#E4E8F0] pb-2.5">
          <span class="text-[#5B6475] font-medium">Penulis / Peneliti</span>
          <span class="col-span-2 font-semibold text-[#0B0F19]">{{ details.examiner }}</span>
        </div>
        <div class="grid grid-cols-3 border-b border-[#E4E8F0] pb-2.5">
          <span class="text-[#5B6475] font-medium">Waktu Audit</span>
          <span class="col-span-2 text-[#5B6475] font-mono tabular-nums">{{ details.auditDate }}</span>
        </div>
        <div class="pt-2 flex flex-wrap items-center gap-2 text-xs">
          <span class="px-3 py-1 rounded-full bg-[#FEF3F2] border border-[#FECDD3] text-[#B91C1C] font-semibold">Leksikal: {{ details.lexicalScore.toFixed(1) }}%</span>
          <span class="px-3 py-1 rounded-full bg-[#FFF1E6] border border-[#FED7AA] text-[#C2410C] font-semibold">Semantik: {{ details.semanticScore.toFixed(1) }}%</span>
          <span class="px-3 py-1 rounded-full bg-[#FEF7D6] border border-[#FEF08A] text-[#A16207] font-semibold">Stilometri: {{ details.styloScore.toFixed(1) }}%</span>
        </div>
        <div class="pt-3 border-t border-[#E4E8F0] flex items-center justify-between">
          <button type="button" @click="emit('copyLink')" class="text-[#1560BD] hover:underline font-semibold cursor-pointer">Salin Tautan</button>
          <button type="button" @click="emit('reset')" class="text-slate-500 hover:text-slate-800 cursor-pointer">Periksa Kode Lain &rarr;</button>
        </div>
      </div>
    </div>
  </div>
</template>
