<script setup lang="ts">
import { useSectionReveal } from "../../composables";
import HeroFeatureChips from "./HeroFeatureChips.vue";
import HeroGlassBackdrop from "./HeroGlassBackdrop.vue";
import HeroParaphraseCard from "./HeroParaphraseCard.vue";
import HeroReportCard from "./HeroReportCard.vue";
import HeroSentencePanel from "./HeroSentencePanel.vue";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.08, rootMargin: "0px" });

function scrollToReport() {
  document.getElementById("laporan-diagnostik")?.scrollIntoView({ behavior: "smooth" });
}
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section relative select-none pb-24 font-sans sm:pb-44"
    :class="{ 'is-visible': isVisible }"
    aria-label="Hero Utama VeriText AI"
  >
    <HeroGlassBackdrop />

    <div class="relative z-10 mx-auto max-w-[1320px] px-3 sm:px-5">
      <div class="vt-reveal-zoom vt-d-3">
        <HeroFeatureChips />
      </div>

      <div class="relative z-20 mx-auto max-w-[980px] px-5 pt-16 text-center sm:pt-24">
        <h1 class="vt-reveal text-[40px] font-semibold leading-[1.06] tracking-[-0.045em] text-[#14111C] sm:text-[60px] lg:text-[68px]">
          Periksa orisinalitas naskah
          <span class="vt-accent block pb-1">kalimat demi kalimat.</span>
        </h1>

        <p class="vt-reveal vt-d-1 mx-auto mt-6 max-w-[520px] text-[16px] leading-[1.65] text-[#4B4757] sm:text-[18px]">
          Unggah naskah, lihat kalimat mana yang mirip sumber lain atau terindikasi ditulis AI, lalu perbaiki langsung.
        </p>

        <div class="vt-reveal vt-d-2 mt-9 flex flex-wrap items-center justify-center gap-3">
          <router-link
            to="/dashboard"
            class="inline-flex h-[52px] cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl active:scale-[0.98]"
          >
            Mulai periksa gratis
          </router-link>
          <button
            type="button"
            @click="scrollToReport"
            class="inline-flex h-[52px] cursor-pointer items-center justify-center rounded-full bg-white px-7 text-[15px] font-semibold text-[#14111C] shadow-lift transition-all duration-300 hover:-translate-y-1 hover:shadow-float active:scale-[0.98]"
          >
            Lihat contoh laporan
          </button>
        </div>
        <p class="vt-reveal vt-d-3 mt-4 text-[13px] text-[#5E5A6B]">5 token gratis saat daftar. Tanpa kartu kredit.</p>
      </div>

      <div class="relative mx-auto mt-16 h-[300px] max-w-[1180px] px-5 sm:h-[372px]">
        <div class="vt-reveal-left vt-d-4 absolute bottom-0 left-0 hidden lg:block">
          <HeroReportCard :active="isVisible" />
        </div>
        <div class="vt-reveal-right vt-d-5 absolute bottom-0 right-0 hidden lg:block">
          <HeroParaphraseCard />
        </div>
        <div class="vt-reveal-zoom vt-d-3 relative mx-auto max-w-[560px]">
          <HeroSentencePanel />
        </div>
      </div>
    </div>
  </section>
</template>
