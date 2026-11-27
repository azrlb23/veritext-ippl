<script setup lang="ts">
import { useSectionReveal } from "../composables";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });

const links = [
  { name: "Ringkasan", to: "/dashboard" },
  { name: "Token", to: "/billing" },
  { name: "Verifikasi Sertifikat", to: "/verify" },
  { name: "Kebijakan Privasi", to: "/privasi" },
  { name: "Ketentuan Layanan", to: "/ketentuan" },
];
</script>

<template>
  <footer
    ref="sectionRef"
    class="vt-section relative mt-16 w-full select-none overflow-hidden font-sans sm:mt-24"
    :class="{ 'is-visible': isVisible }"
    aria-label="Footer VeriText AI"
  >
    <div class="relative mx-auto max-w-[1240px] px-6 pt-8 sm:px-8">
      <div class="flex flex-col gap-12 md:flex-row md:items-start md:justify-between">
        <div class="vt-reveal-left max-w-md">
          <router-link
            to="/"
            class="inline-flex h-11 items-center rounded text-[24px] font-semibold tracking-[-0.04em] text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          >
            VeriText <span class="ml-1.5 text-[#0F766E]">AI</span>
          </router-link>
          <p class="mt-4 text-[15px] leading-[1.65] text-[#4B4757]">
            Platform audit orisinalitas naskah dengan pemeriksaan kata, makna, dan gaya tulisan.
          </p>
          <router-link
            to="/dashboard"
            class="vt-btn-dark mt-6 inline-flex h-11 cursor-pointer items-center rounded-full px-6 text-[13.5px] font-semibold"
          >
            Mulai periksa gratis
          </router-link>
        </div>

        <nav class="vt-reveal-right vt-d-1 md:min-w-[220px]" aria-label="Tautan singkat">
          <h5 class="text-[13px] font-medium text-[#5E5A6B]">Tautan singkat</h5>
          <ul class="mt-2 text-[15px] text-[#14111C]">
            <li v-for="l in links" :key="l.to">
              <router-link
                :to="l.to"
                class="inline-flex min-h-[44px] items-center rounded transition-colors duration-200 hover:text-[#0F766E] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
              >
                {{ l.name }}
              </router-link>
            </li>
          </ul>
        </nav>
      </div>

      <p class="vt-reveal vt-d-2 mt-14 text-[13px] text-[#5E5A6B]">&copy; 2026 Tim Pengembang VeriText AI. Seluruh hak dilindungi.</p>
    </div>

    <div class="vt-reveal vt-d-3 pointer-events-none relative mt-6 h-[clamp(70px,13vw,190px)] overflow-hidden text-center" aria-hidden="true">
      <span
        class="block bg-gradient-to-b from-[#0F766E]/25 to-transparent bg-clip-text text-[clamp(90px,21vw,320px)] font-semibold leading-[0.9] tracking-[-0.06em] text-transparent"
      >VeriText AI</span>
    </div>
  </footer>
</template>
