<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

// Isi panel kanan halaman masuk dan daftar. Ubin kaca ada di latar halaman (LandingBackdrop).
const chips: Array<{ title: string; pos: string; icon: VtIconName }> = [
  { title: "Tiga lapis pemeriksaan", pos: "left-[10%] top-[22%] -rotate-6", icon: "semantic" },
  { title: "Laporan per kalimat", pos: "right-[8%] top-[33%] rotate-3", icon: "lexical" },
  { title: "Sertifikat terverifikasi QR", pos: "left-[16%] bottom-[22%] rotate-2", icon: "qr-badge" },
];
</script>

<template>
  <div class="pointer-events-none relative flex h-full w-full items-center justify-center overflow-hidden" aria-hidden="true">
    <div class="text-center">
      <div class="text-[clamp(44px,5vw,72px)] font-semibold leading-none tracking-[-0.05em] text-[#14111C]">
        VeriText <span class="text-[#0F766E] drop-shadow-[0_2px_14px_rgba(255,255,255,0.75)]">AI</span>
      </div>
      <p class="pointer-events-auto select-text mx-auto mt-5 max-w-[330px] text-[14.5px] font-medium leading-[1.6] text-[#14111C]">
        Periksa orisinalitas naskah, <span class="font-semibold text-[#0F766E]">kalimat demi kalimat.</span>
      </p>
    </div>

    <div
      v-for="c in chips"
      :key="c.title"
      class="absolute flex w-max items-center gap-2.5 whitespace-nowrap rounded-full bg-white px-4 py-2.5 shadow-float"
      :class="c.pos"
    >
      <VtIcon :name="c.icon" tone="current" class="h-[18px] w-[18px] shrink-0 text-[#0F766E]" />
      <span class="text-[13.5px] font-semibold text-[#14111C]">{{ c.title }}</span>
    </div>
  </div>
</template>
