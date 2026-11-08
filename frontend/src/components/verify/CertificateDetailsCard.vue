<script setup lang="ts">
import { computed } from "vue";
import VerifySeal from "./VerifySeal.vue";

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

const props = defineProps<{ details: CertificateDetails }>();
const emit = defineEmits<{ (e: "reset"): void; (e: "copyLink"): void }>();

const composite = computed(() => Math.min(100, Math.max(0, props.details.compositeScore)));
const originality = computed(() => Math.max(0, Math.min(100, 100 - composite.value)));
const isPassed = computed(() => composite.value <= 20);
const ringColor = computed(() => (isPassed.value ? "#8A3FE0" : "#C2410C"));
const fmt = (v: number) => v.toFixed(1).replace(".", ",");

const statusLabel = computed(() => {
  if (composite.value <= 20) return "Orisinalitas baik";
  if (composite.value <= 40) return "Perlu tinjauan";
  return "Kemiripan tinggi, perlu revisi";
});

const bars = computed(() => [
  { label: "Kecocokan kata", value: props.details.lexicalScore, bar: "bg-[#EF4444]" },
  { label: "Kecocokan makna", value: props.details.semanticScore, bar: "bg-[#F97316]" },
  { label: "Pola tulisan AI", value: props.details.styloScore, bar: "bg-[#EAB308]" },
]);

const rows = computed(() => [
  { k: "Judul naskah", v: props.details.title },
  { k: "Pemilik naskah", v: props.details.examiner },
  { k: "Waktu audit", v: props.details.auditDate },
]);
</script>

<template>
  <div class="relative mx-auto max-w-[980px] rounded-[40px] bg-white p-7 pt-10 shadow-float sm:p-12 font-sans select-none">
    <div class="absolute -top-9 right-5 sm:right-10"><VerifySeal /></div>
    <div class="flex items-center gap-2 text-[14px] font-semibold text-[#15803D]">
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>
      Sertifikat terverifikasi
    </div>

    <div class="mt-9 grid items-center gap-10 md:grid-cols-12 md:gap-12">
      <div class="md:col-span-5">
        <div class="relative mx-auto h-[210px] w-[210px] md:mx-0">
          <svg class="h-full w-full -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EFEAF6" stroke-width="2.6" />
            <circle cx="18" cy="18" r="15.9" fill="none" :stroke="ringColor" stroke-width="2.6" stroke-linecap="round" :stroke-dasharray="`${originality} 100`" />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-[50px] font-semibold leading-none tracking-[-0.05em] text-[#14111C] tabular-nums">{{ fmt(originality) }}%</span>
            <span class="mt-1.5 text-[12px] text-[#5E5A6B]">Skor orisinalitas</span>
          </div>
        </div>
        <p class="mt-5 text-center text-[16px] font-semibold md:text-left" :class="isPassed ? 'text-[#14111C]' : 'text-[#C2410C]'">{{ statusLabel }}</p>
        <p class="mt-1 text-center text-[13px] text-[#5E5A6B] md:text-left">Kesamaan komposit {{ fmt(composite) }}%</p>
      </div>

      <div class="md:col-span-7">
        <dl class="space-y-5">
          <div v-for="r in rows" :key="r.k">
            <dt class="text-[12.5px] text-[#5E5A6B]">{{ r.k }}</dt>
            <dd class="mt-0.5 text-[17px] font-semibold leading-snug tracking-[-0.02em] text-[#14111C]">{{ r.v }}</dd>
          </div>
        </dl>

        <div class="mt-8 space-y-4">
          <div v-for="b in bars" :key="b.label">
            <div class="flex items-baseline justify-between text-[13.5px]">
              <span class="font-medium text-[#14111C]">{{ b.label }}</span>
              <span class="font-semibold text-[#14111C] tabular-nums">{{ fmt(b.value) }}%</span>
            </div>
            <div class="mt-2 h-1.5 w-full rounded-full bg-[#EFEAF6]">
              <div class="h-1.5 rounded-full" :class="b.bar" :style="{ width: Math.min(100, b.value) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <button
        type="button"
        @click="emit('copyLink')"
        class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-7 text-[14px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 sm:h-11 sm:w-auto"
      >
        Bagikan tautan
      </button>
      <button type="button" @click="emit('reset')" class="h-12 w-full cursor-pointer text-[14px] font-medium text-[#4B4757] transition-colors hover:text-[#6D28D9] sm:h-auto sm:w-auto">
        Periksa kode lain
      </button>
    </div>
  </div>
</template>
