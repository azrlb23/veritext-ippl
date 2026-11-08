<script setup lang="ts">
import ShowcaseFindings from "./ShowcaseFindings.vue";
import ShowcaseManuscriptFragment from "./ShowcaseManuscriptFragment.vue";
import ShowcaseMetricCards from "./ShowcaseMetricCards.vue";
import ShowcaseScoreGauge from "./ShowcaseScoreGauge.vue";
</script>

<template>
  <section
    id="laporan-diagnostik"
    class="relative mx-auto max-w-[1240px] scroll-mt-24 select-none px-4 py-20 font-sans sm:px-6 sm:py-28"
    aria-label="Contoh laporan"
  >
    <div class="mx-auto mb-14 max-w-2xl text-center">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Laporan diagnostik</p>
      <h2 class="mt-3 text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#14111C] sm:text-[52px]">
        Satu laporan untuk <span class="vt-accent">seluruh analisis.</span>
      </h2>
      <p class="mt-5 text-[16px] leading-[1.65] text-[#4B4757]">
        Pemeriksaan kata, makna, dan pola tulisan dirangkum dalam satu laporan yang bisa ditelusuri sampai ke kalimat dan sumbernya.
      </p>
    </div>

    <div class="grid items-center gap-14 lg:grid-cols-12 lg:gap-10">
      <div class="lg:col-span-4 lg:pl-4">
        <ShowcaseFindings />
        <router-link
          to="/dashboard"
          class="mt-10 inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-6 text-[13.5px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5"
        >
          Buka workspace
        </router-link>
      </div>

      <div class="lg:col-span-8 lg:pb-16 lg:pt-12">
        <div class="relative">
          <ShowcaseManuscriptFragment class="lg:mr-12 lg:-rotate-[1.2deg]" />
          <ShowcaseScoreGauge class="mt-4 lg:absolute lg:-right-4 lg:-top-12 lg:mt-0 lg:w-[270px] lg:rotate-[3deg]" />
          <ShowcaseMetricCards class="mt-4 lg:absolute lg:-bottom-14 lg:right-2 lg:mt-0" />
        </div>
      </div>
    </div>
  </section>
</template>
