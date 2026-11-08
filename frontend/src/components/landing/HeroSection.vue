<script setup lang="ts">
import HeroFeatureChips from "./HeroFeatureChips.vue";
import HeroParaphraseCard from "./HeroParaphraseCard.vue";
import HeroReportCard from "./HeroReportCard.vue";
import HeroSentencePanel from "./HeroSentencePanel.vue";

function scrollToReport() {
  document.getElementById("laporan-diagnostik")?.scrollIntoView({ behavior: "smooth" });
}
</script>

<template>
  <section class="px-3 sm:px-5 select-none font-sans" aria-label="Hero Utama VeriText AI">
    <div class="relative mx-auto max-w-[1320px] overflow-hidden rounded-[40px] bg-[linear-gradient(180deg,#FFFFFF_0%,#F4F6FF_52%,#E3E8FF_100%)]">
      <HeroFeatureChips />

      <div class="relative z-20 mx-auto max-w-[980px] px-5 pt-16 text-center sm:pt-24">
        <h1 class="text-[40px] font-semibold leading-[1.06] tracking-[-0.045em] text-[#0B0F19] sm:text-[60px] lg:text-[68px]">
          Periksa orisinalitas naskah
          <span class="block pb-1 italic font-medium bg-gradient-to-r from-[#1A73D9] to-[#7C5CFA] bg-clip-text text-transparent">
            kalimat demi kalimat.
          </span>
        </h1>

        <p class="mx-auto mt-6 max-w-[520px] text-[16px] leading-[1.65] text-[#4A5266] sm:text-[18px]">
          Unggah naskah, lihat kalimat mana yang mirip sumber lain atau terindikasi ditulis AI, lalu perbaiki langsung.
        </p>

        <div class="mt-9 flex flex-wrap items-center justify-center gap-3">
          <router-link
            to="/dashboard"
            class="inline-flex h-[52px] cursor-pointer items-center justify-center rounded-full bg-[#0B0F19] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
          >
            Mulai periksa gratis
          </router-link>
          <button
            type="button"
            @click="scrollToReport"
            class="inline-flex h-[52px] cursor-pointer items-center justify-center rounded-full bg-white px-7 text-[15px] font-semibold text-[#0B0F19] shadow-lift transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
          >
            Lihat contoh laporan
          </button>
        </div>
        <p class="mt-4 text-[13px] text-[#6B7385]">5 token gratis saat daftar. Tanpa kartu kredit.</p>
      </div>

      <div class="relative mx-auto mt-16 h-[300px] max-w-[1180px] px-5 sm:h-[372px]">
        <div class="absolute bottom-[8px] left-0 hidden lg:block">
          <HeroReportCard />
        </div>
        <div class="absolute bottom-[-26px] right-0 hidden lg:block">
          <HeroParaphraseCard />
        </div>
        <div class="relative mx-auto max-w-[560px]">
          <HeroSentencePanel />
        </div>
      </div>
    </div>
  </section>
</template>
