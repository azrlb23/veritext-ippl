<script setup lang="ts">
import { ref } from "vue";
import { useSectionReveal } from "../../composables";
import ShowcaseFindings from "./ShowcaseFindings.vue";
import ShowcaseManuscriptFragment from "./ShowcaseManuscriptFragment.vue";
import ShowcaseMetricCards from "./ShowcaseMetricCards.vue";
import ShowcaseScoreGauge from "./ShowcaseScoreGauge.vue";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.12 });
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
    ref="sectionRef"
    class="vt-section relative mx-auto max-w-[1240px] scroll-mt-24 select-none px-4 py-20 font-sans sm:px-6 sm:py-28"
    :class="{ 'is-visible': isVisible }"
    aria-label="Contoh laporan"
  >
    <div class="mx-auto mb-14 max-w-2xl text-center">
      <p class="vt-reveal text-[14px] font-medium text-[#5E5A6B]">Laporan diagnostik</p>
      <h2 class="vt-reveal vt-d-1 mt-3 text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#14111C] sm:text-[52px]">
        Satu laporan untuk seluruh analisis.
      </h2>
      <p class="vt-reveal vt-d-2 mt-5 text-[16px] leading-[1.65] text-[#4B4757]">
        Pemeriksaan kata, makna, dan pola tulisan dirangkum dalam satu laporan yang bisa ditelusuri sampai ke kalimat dan sumbernya.
      </p>
    </div>

    <div class="grid items-center gap-14 lg:grid-cols-12 lg:gap-10">
      <div class="lg:col-span-4 lg:pl-4">
        <ShowcaseFindings />
        <div class="vt-reveal vt-d-4 mt-10">
          <router-link
            to="/dashboard"
            class="vt-btn-dark inline-flex h-11 cursor-pointer items-center rounded-full px-6 text-[13.5px] font-semibold"
          >
            Buka workspace
          </router-link>
        </div>
      </div>

      <div class="lg:col-span-8 lg:pb-16 lg:pt-12">
        <div class="relative">
          <div class="vt-reveal-zoom vt-d-2">
            <ShowcaseManuscriptFragment
              class="lg:mr-12 lg:-rotate-[1.2deg] transition-all duration-500 hover:rotate-0 hover:shadow-2xl"
              :external-filter="activeFilter"
              @update:filter="activeFilter = $event"
            />
          </div>
          <div class="mt-4 lg:absolute lg:-right-4 lg:-top-12 lg:mt-0 lg:w-[270px] vt-reveal-right vt-d-3">
            <ShowcaseScoreGauge :active="isVisible" class="lg:rotate-[3deg]" />
          </div>
          <div class="mt-4 lg:absolute lg:-bottom-14 lg:right-2 lg:mt-0 vt-reveal vt-d-4">
            <ShowcaseMetricCards
              :active="isVisible"
              :active-filter="activeFilter"
              @select="handleMetricSelect"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
