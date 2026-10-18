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
  <div class="bg-white border border-[#ededed] rounded-[14px] p-6 sm:p-8 shadow-audyr-subtle space-y-6">
    <div class="flex items-center justify-between border-b border-[#ededed] pb-4">
      <h2 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
        Ringkasan Hasil Uji Integritas Akademik
      </h2>
      <span class="text-[11px] font-medium tracking-tight px-3 py-0.5 rounded-full bg-[#ededed] text-audyr-ink">
        Publik &bull; Read-Only
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
      <div class="flex justify-center md:col-span-1">
        <SimilarityGauge :score="details.compositeScore" />
      </div>

      <div class="md:col-span-2 space-y-3 text-xs">
        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-medium tracking-tight">Judul Naskah</span>
          <span class="col-span-2 font-semibold text-audyr-ink">{{ details.title }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-medium tracking-tight">Nama Pemeriksa</span>
          <span class="col-span-2 font-medium text-audyr-ink">{{ details.examiner }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-medium tracking-tight">Institusi / Afiliasi</span>
          <span class="col-span-2 text-audyr-slate">{{ details.institution }}</span>
        </div>

        <div class="grid grid-cols-3 border-b border-[#ededed] pb-2">
          <span class="text-audyr-ash font-medium tracking-tight">Waktu Pengujian</span>
          <span class="col-span-2 text-audyr-slate font-mono">{{ details.auditDate }}</span>
        </div>

        <div class="pt-2">
          <div class="text-[11px] font-semibold text-audyr-ash uppercase tracking-tight mb-2">Rincian per Tier:</div>
          <div class="grid grid-cols-3 gap-2 text-center text-[11px]">
            <div class="p-2.5 bg-red-50 text-red-700 border border-red-200 rounded-[8px] font-medium">
              Tier 1: {{ details.lexicalScore }}%
            </div>
            <div class="p-2.5 bg-orange-50 text-orange-700 border border-orange-200 rounded-[8px] font-medium">
              Tier 2: {{ details.semanticScore }}%
            </div>
            <div class="p-2.5 bg-yellow-50 text-yellow-800 border border-yellow-200 rounded-[8px] font-medium">
              Tier 3: {{ details.styloScore }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
