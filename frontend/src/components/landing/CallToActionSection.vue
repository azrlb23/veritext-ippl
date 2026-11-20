<script setup lang="ts">
import { useSectionReveal } from "../../composables";
import CtaBubbleWall from "./CtaBubbleWall.vue";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.15 });
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section select-none px-3 pb-16 font-sans sm:px-5 sm:pb-24"
    :class="{ 'is-visible': isVisible }"
    aria-label="Ajakan bertindak"
  >
    <div class="mx-auto max-w-[1320px] px-6 py-20 text-center sm:py-24">
      <h2 class="vt-reveal-zoom mx-auto max-w-2xl text-[32px] font-semibold leading-[1.12] tracking-[-0.04em] text-[#14111C] sm:text-[48px]">
        Sering khawatir sebelum kumpul naskah?
      </h2>

      <CtaBubbleWall class="vt-reveal vt-d-1 mt-10" />

      <div class="mt-8 md:mt-4">
        <h3 class="vt-reveal vt-d-2 text-[28px] font-semibold leading-[1.15] tracking-[-0.035em] text-[#14111C] sm:text-[38px]">
          Kamu tidak sendirian.
        </h3>
        <p class="vt-reveal vt-d-2 mx-auto mt-3 max-w-md text-[15.5px] leading-[1.6] text-[#4B4757]">
          Periksa kemiripan, deteksi pola AI, dan perbaiki naskah secara privat sebelum dikumpulkan.
        </p>
        <div class="vt-reveal vt-d-3 mt-7">
          <router-link
            to="/dashboard"
            class="inline-flex h-[54px] cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-9 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
          >
            Mulai periksa gratis
          </router-link>
        </div>
        <p class="vt-reveal vt-d-3 mt-4 text-[13px] text-[#5E5A6B]">
          5 token gratis saat daftar. Tanpa kartu kredit.
        </p>
      </div>
    </div>
  </section>
</template>
