<script setup lang="ts">
// Isi panel kanan halaman masuk dan daftar. Ubin kaca ada di latar halaman (LandingBackdrop).
const chips = [
  { title: "Tiga lapis pemeriksaan", sub: "Kata, makna, pola tulisan", pos: "left-[10%] top-[22%] -rotate-6", icon: "M4 7l8-4 8 4-8 4-8-4zM4 12l8 4 8-4M4 17l8 4 8-4" },
  { title: "Laporan per kalimat", sub: "Sorotan warna yang bisa ditelusuri", pos: "right-[8%] top-[33%] rotate-3", icon: "M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6" },
  { title: "Sertifikat terverifikasi QR", sub: "Dicek siapa saja, dari ponsel", pos: "left-[16%] bottom-[22%] rotate-2", icon: "M5 5h5v5H5zM14 5h5v5h-5zM5 14h5v5H5zM14 14h2v2h-2zM18 14v5h-5" },
];
</script>

<template>
  <div class="pointer-events-none relative flex h-full w-full items-center justify-center overflow-hidden" aria-hidden="true">
    <div class="text-center">
      <div class="text-[clamp(44px,5vw,72px)] font-semibold leading-none tracking-[-0.05em] text-[#14111C]">
        VeriText <span class="vt-accent">AI</span>
      </div>
      <p class="mx-auto mt-4 max-w-[300px] text-[15px] leading-[1.6] text-[#4B4757]">Periksa orisinalitas naskah, kalimat demi kalimat.</p>
    </div>

    <div
      v-for="c in chips"
      :key="c.title"
      class="absolute flex w-max items-center gap-3 whitespace-nowrap rounded-[20px] bg-white px-4 py-3.5 shadow-float"
      :class="c.pos"
    >
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[13px] bg-[#F3EEFA] text-[#14111C]">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" :d="c.icon" />
        </svg>
      </div>
      <div>
        <div class="text-[13.5px] font-semibold text-[#14111C]">{{ c.title }}</div>
        <div class="text-[11.5px] text-[#5E5A6B]">{{ c.sub }}</div>
      </div>
    </div>
  </div>
</template>
