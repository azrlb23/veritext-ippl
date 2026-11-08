<script setup lang="ts">
import { ref } from "vue";
import ShowcaseFindings from "./ShowcaseFindings.vue";
import ShowcaseManuscriptFragment from "./ShowcaseManuscriptFragment.vue";
import ShowcaseMetricCards from "./ShowcaseMetricCards.vue";
import ShowcaseScoreGauge from "./ShowcaseScoreGauge.vue";

const activeFilter = ref<"all" | "lex" | "sem" | "sty">("all");

function handleMetricSelect(key: string) {
  if (activeFilter.value === key) {
    activeFilter.value = "all";
  } else {
    activeFilter.value = key as any;
  }
}
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
          class="mt-10 inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-6 text-[13.5px] font-semibold text-white shadow-btn-dark transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl active:scale-[0.98]"
        >
          Buka workspace
        </router-link>
      </div>

      <div class="lg:col-span-8 lg:pb-16 lg:pt-12">
        <div class="relative">
          <ShowcaseManuscriptFragment
            class="lg:mr-12 lg:-rotate-[1.2deg] transition-all duration-500 hover:rotate-0 hover:shadow-2xl"
            :external-filter="activeFilter"
            @update:filter="activeFilter = $event"
          />
          <ShowcaseScoreGauge class="mt-4 lg:absolute lg:-right-4 lg:-top-12 lg:mt-0 lg:w-[270px] lg:rotate-[3deg]" />
          <ShowcaseMetricCards
            class="mt-4 lg:absolute lg:-bottom-14 lg:right-2 lg:mt-0"
            :active-filter="activeFilter"
            @select="handleMetricSelect"
          />
        </div>
      </div>
    </div>
  </section>
</template>
