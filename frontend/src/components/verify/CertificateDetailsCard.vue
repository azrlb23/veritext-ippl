<script setup lang="ts">
import SimilarityGauge from "../SimilarityGauge.vue";

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

defineProps<Props>();
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[24px] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] space-y-6">
    <div class="flex items-center justify-between border-b border-[#ededed] pb-4">
      <h2 class="text-sm font-semibold uppercase tracking-tight text-[#17191c]">
        Ringkasan Hasil Uji Integritas Akademik
      </h2>
      <span class="text-[11px] italic font-medium tracking-tight px-3 py-0.5 rounded-full bg-[#f2f2f3] text-[#17191c]">
        Publik &bull; Read-Only
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
      <div class="flex justify-center md:col-span-1">
        <SimilarityGauge :score="details.compositeScore" />
      </div>

      <div class="md:col-span-2 space-y-3 text-xs">
        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-bold tracking-tight">Judul Naskah</span>
          <span class="col-span-2 font-bold text-audyr-ink">{{ details.title }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-bold tracking-tight">Nama Pemeriksa</span>
          <span class="col-span-2 font-medium text-audyr-ink">{{ details.examiner }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-bold tracking-tight">Institusi / Afiliasi</span>
          <span class="col-span-2 text-audyr-slate">{{ details.institution }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-bold tracking-tight">Waktu Pengujian</span>
          <span class="col-span-2 text-audyr-slate tabular-nums font-medium">{{ details.auditDate }}</span>
        </div>

        <div class="pt-2">
          <div class="text-[11px] font-extrabold text-audyr-ash uppercase tracking-tight mb-2">Rincian per Tier:</div>
          <div class="grid grid-cols-3 gap-2 text-center text-[11px]">
            <div class="p-2.5 bg-red-50 text-red-700 border border-red-200 rounded-[8px] font-bold">
              Tier 1: <span class="font-extrabold tabular-nums">{{ details.lexicalScore }}%</span>
            </div>
            <div class="p-2.5 bg-orange-50 text-orange-700 border border-orange-200 rounded-[8px] font-bold">
              Tier 2: <span class="font-extrabold tabular-nums">{{ details.semanticScore }}%</span>
            </div>
            <div class="p-2.5 bg-yellow-50 text-yellow-800 border border-yellow-200 rounded-[8px] font-bold">
              Tier 3: <span class="font-extrabold tabular-nums">{{ details.styloScore }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
