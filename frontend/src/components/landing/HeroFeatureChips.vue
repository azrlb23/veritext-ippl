<script setup lang="ts">
// Empat chip fitur kecil yang melayang di sisi judul (hanya layar lebar).
const chips = [
  { title: "Cek kata", sub: "Kecocokan persis", pos: "left-[1%] top-[76px] -rotate-6", icon: "M4 7h16M4 12h16M4 17h10" },
  { title: "Cek makna", sub: "Parafrasa terdeteksi", pos: "left-[5%] top-[236px] rotate-3", icon: "M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1" },
  { title: "Teks AI", sub: "Pola tulisan mesin", pos: "right-[1%] top-[68px] rotate-6", icon: "M9 3v2M15 3v2M9 19v2M15 19v2M3 9h2M3 15h2M19 9h2M19 15h2M7 7h10v10H7z" },
  { title: "Parafrase", sub: "Tiga gaya penulisan", pos: "right-[5%] top-[228px] -rotate-3", icon: "M4 12a8 8 0 0113.7-5.6L20 8M20 4v4h-4M20 12a8 8 0 01-13.7 5.6L4 16M4 20v-4h4" },
];
</script>

<template>
  <div class="pointer-events-none hidden xl:block" aria-hidden="true">
    <div
      v-for="c in chips"
      :key="c.title"
      class="absolute flex w-max items-center gap-3 whitespace-nowrap rounded-[18px] bg-white px-3.5 py-3 shadow-lift"
      :class="c.pos"
    >
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-[11px] bg-[#F3EEFA] text-[#14111C]">
        <svg class="h-[18px] w-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" :d="c.icon" />
        </svg>
      </div>
      <div>
        <div class="text-[12.5px] font-semibold text-[#14111C]">{{ c.title }}</div>
        <div class="text-[10.5px] text-[#5E5A6B]">{{ c.sub }}</div>
      </div>
    </div>
  </div>
</template>
