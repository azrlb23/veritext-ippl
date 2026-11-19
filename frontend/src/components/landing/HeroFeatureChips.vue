<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

const chips: Array<{ title: string; sub: string; pos: string; anim: string; icon: VtIconName }> = [
  { title: "Cek kata", sub: "Kecocokan persis", pos: "left-[1%] top-[76px] -rotate-6", anim: "animate-float-a", icon: "text-match" },
  { title: "Cek makna", sub: "Parafrasa terdeteksi", pos: "left-[5%] top-[236px] rotate-3", anim: "animate-float-b", icon: "meaning" },
  { title: "Teks AI", sub: "Pola tulisan mesin", pos: "right-[1%] top-[68px] rotate-6", anim: "animate-float-b", icon: "stylometric" },
  { title: "Parafrase", sub: "Tiga gaya penulisan", pos: "right-[5%] top-[228px] -rotate-3", anim: "animate-float-a", icon: "rewrite" },
];
</script>

<template>
  <div class="pointer-events-none hidden xl:block" aria-hidden="true">
    <div
      v-for="c in chips"
      :key="c.title"
      class="pointer-events-auto absolute flex w-max items-center gap-3 whitespace-nowrap rounded-[18px] bg-white px-3.5 py-3 shadow-lift transition-all duration-300 hover:scale-105 hover:shadow-float cursor-default"
      :class="[c.pos, c.anim]"
    >
      <VtIcon :name="c.icon" class="h-5 w-5 shrink-0 text-[#14111C]" />
      <div>
        <div class="text-[12.5px] font-semibold text-[#14111C]">{{ c.title }}</div>
        <div class="text-[10.5px] text-[#5E5A6B]">{{ c.sub }}</div>
      </div>
    </div>
  </div>
</template>
