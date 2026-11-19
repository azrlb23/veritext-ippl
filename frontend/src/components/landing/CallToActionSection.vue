<script setup lang="ts">
import { useSectionReveal } from "../../composables";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.15 });
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section select-none px-3 pb-16 font-sans sm:px-5 sm:pb-24"
    :class="{ 'is-visible': isVisible }"
    aria-label="Ajakan bertindak"
  >
    <div class="mx-auto max-w-[1320px] px-6 py-20 text-center sm:py-28">
      <h2 class="vt-reveal-zoom mx-auto max-w-3xl text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[56px]">
        Pastikan tulisanmu
        <span class="vt-accent block">benar-benar asli.</span>
      </h2>
      <p class="vt-reveal vt-d-1 mx-auto mt-6 max-w-xl text-[16px] leading-[1.65] text-[#4B4757] sm:text-[18px]">
        Periksa naskah dengan tiga lapis pemeriksaan dan terima laporan yang bisa dipertanggungjawabkan.
      </p>
      <div class="vt-reveal vt-d-2 mt-9">
        <router-link
          to="/dashboard"
          class="inline-flex h-[54px] cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-9 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
        >
          Mulai periksa gratis
        </router-link>
      </div>
      <p class="vt-reveal vt-d-3 mt-4 text-[13px] text-[#5E5A6B]">5 token gratis saat daftar. Tanpa kartu kredit.</p>
    </div>
  </section>
</template>
