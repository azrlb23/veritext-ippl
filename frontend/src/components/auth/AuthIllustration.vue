<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

// Isi panel kanan halaman masuk dan daftar. Ubin kaca ada di latar halaman (LandingBackdrop).
const chips: Array<{ title: string; sub: string; pos: string; icon: VtIconName }> = [
  { title: "Tiga lapis pemeriksaan", sub: "Kata, makna, pola tulisan", pos: "left-[10%] top-[22%] -rotate-6", icon: "semantic" },
  { title: "Laporan per kalimat", sub: "Sorotan warna yang bisa ditelusuri", pos: "right-[8%] top-[33%] rotate-3", icon: "lexical" },
  { title: "Sertifikat terverifikasi QR", sub: "Dicek siapa saja, dari ponsel", pos: "left-[16%] bottom-[22%] rotate-2", icon: "qr-badge" },
];
</script>

<template>
  <div class="pointer-events-none relative flex h-full w-full items-center justify-center overflow-hidden" aria-hidden="true">
    <div class="text-center">
      <div class="text-[clamp(44px,5vw,72px)] font-semibold leading-none tracking-[-0.05em] text-[#14111C]">
        VeriText <span class="vt-accent drop-shadow-[0_2px_14px_rgba(255,255,255,0.75)]">AI</span>
      </div>
      <p class="pointer-events-auto select-text mx-auto mt-5 inline-block max-w-[330px] rounded-[20px] bg-white/85 px-5 py-3 text-[14.5px] font-medium leading-[1.6] text-[#14111C] shadow-lift backdrop-blur-md">
        Periksa orisinalitas naskah, <span class="rounded-[6px] bg-[#EDE3FA] px-1.5 py-0.5 font-semibold text-[#6D28D9]">kalimat demi kalimat.</span>
      </p>
    </div>

    <div
      v-for="c in chips"
      :key="c.title"
      class="absolute flex w-max items-center gap-3 whitespace-nowrap rounded-[20px] bg-white px-4 py-3.5 shadow-float"
      :class="c.pos"
    >
      <VtIcon :name="c.icon" class="h-5 w-5 shrink-0 text-[#14111C]" />
      <div>
        <div class="text-[13.5px] font-semibold text-[#14111C]">{{ c.title }}</div>
        <div class="text-[12px] text-[#4B4757]">{{ c.sub }}</div>
      </div>
    </div>
  </div>
</template>
