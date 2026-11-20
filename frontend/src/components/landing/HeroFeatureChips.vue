<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

const chips: Array<{ title: string; pos: string; anim: string; icon: VtIconName }> = [
  { title: "Cek kata", pos: "left-[2%] top-[24px] -rotate-6", anim: "animate-float-a", icon: "text-match" },
  { title: "Cek makna", pos: "left-[1%] top-[256px] rotate-3", anim: "animate-float-b", icon: "meaning" },
  { title: "Teks AI", pos: "right-[6%] top-[44px] rotate-6", anim: "animate-float-b", icon: "stylometric" },
  { title: "Parafrase", pos: "right-[8%] top-[242px] -rotate-3", anim: "animate-float-a", icon: "rewrite" },
];

const tiles: Array<{ icon: VtIconName; cls: string }> = [
  { icon: "meaning", cls: "left-[11%] top-[132px] h-10 w-10 rounded-[13px] rotate-12 animate-float-b text-[#0F766E]" },
  { icon: "stylometric", cls: "right-[1%] top-[156px] h-11 w-11 rounded-[14px] -rotate-12 animate-float-a text-[#D97706]" },
  { icon: "verified", cls: "right-[2%] top-[336px] h-9 w-9 rounded-[12px] rotate-12 animate-float-b text-[#14111C]" },
];

function scrollToShowcase() {
  document.getElementById("laporan-diagnostik")?.scrollIntoView({ behavior: "smooth" });
}
</script>

<template>
  <div class="pointer-events-none hidden xl:block" aria-hidden="true">
    <div
      v-for="c in chips"
      :key="c.title"
      class="pointer-events-auto absolute flex w-max cursor-pointer items-center gap-2.5 whitespace-nowrap rounded-full bg-white px-4 py-2.5 shadow-lift transition-all duration-300 hover:scale-110 hover:-translate-y-1.5 hover:rotate-0 hover:shadow-float"
      :class="[c.pos, c.anim]"
      @click="scrollToShowcase"
    >
      <VtIcon :name="c.icon" tone="current" class="h-[18px] w-[18px] shrink-0 text-[#0F766E]" />
      <span class="text-[12.5px] font-semibold text-[#14111C]">{{ c.title }}</span>
    </div>
    <div
      v-for="(t, i) in tiles"
      :key="`${t.icon}-${i}`"
      class="pointer-events-auto absolute flex cursor-pointer items-center justify-center bg-white shadow-lift transition-all duration-300 hover:scale-110 hover:-translate-y-1.5 hover:rotate-0 hover:shadow-float"
      :class="t.cls"
      @click="scrollToShowcase"
    >
      <VtIcon :name="t.icon" tone="current" class="h-[18px] w-[18px]" />
    </div>
  </div>
</template>
