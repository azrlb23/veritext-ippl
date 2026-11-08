<script setup lang="ts">
import ShowcaseManuscriptFragment from "./ShowcaseManuscriptFragment.vue";
import ShowcaseScoreGauge from "./ShowcaseScoreGauge.vue";

const findings = [
  { title: "Kecocokan kata", text: "12 penggalan kalimat identik dengan dokumen arsip internal 2023." },
  { title: "Kecocokan makna", text: "4 kalimat diubah susunannya, tetapi maknanya tetap sangat dekat dengan sumber." },
  { title: "Pola tulisan", text: "Variasi panjang kalimat dan kosakata menunjukkan tulisan manusia." },
];
</script>

<template>
  <section
    id="laporan-diagnostik"
    class="mx-auto max-w-[1320px] scroll-mt-24 select-none px-3 py-16 font-sans sm:px-5 sm:py-24"
    aria-label="Contoh laporan"
  >
    <div class="mx-auto mb-12 max-w-2xl text-center">
      <p class="text-[14px] font-medium text-[#6B7385]">Laporan diagnostik</p>
      <h2 class="mt-3 text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#0B0F19] sm:text-[52px]">
        Satu laporan untuk <span class="vt-accent">seluruh analisis.</span>
      </h2>
      <p class="mt-5 text-[16px] leading-[1.65] text-[#4A5266]">
        Pemeriksaan kata, makna, dan pola tulisan dirangkum dalam satu laporan yang bisa ditelusuri sampai ke kalimat dan sumbernya.
      </p>
    </div>

    <div class="vt-stage rounded-[40px] p-4 sm:p-8">
      <div class="mb-5 flex items-center justify-between gap-3 px-2">
        <div class="min-w-0">
          <div class="truncate text-[15px] font-semibold text-[#0B0F19]">Naskah-Laporan-2026.pdf</div>
          <div class="text-[12.5px] text-[#6B7385]">Diperiksa dalam 1,1 detik. Contoh tampilan.</div>
        </div>
        <router-link
          to="/dashboard"
          class="inline-flex h-10 shrink-0 cursor-pointer items-center rounded-full bg-[#0B0F19] px-5 text-[13px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5"
        >
          Buka workspace
        </router-link>
      </div>

      <div class="grid grid-cols-1 items-stretch gap-4 lg:grid-cols-12 lg:gap-5">
        <ShowcaseManuscriptFragment />
        <ShowcaseScoreGauge />
      </div>

      <div class="mt-4 grid grid-cols-1 gap-6 rounded-[28px] bg-white p-6 shadow-lift sm:p-8 md:grid-cols-3 lg:mt-5">
        <div v-for="f in findings" :key="f.title">
          <div class="text-[14.5px] font-semibold text-[#0B0F19]">{{ f.title }}</div>
          <p class="mt-1.5 text-[13.5px] leading-[1.6] text-[#4A5266]">{{ f.text }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
