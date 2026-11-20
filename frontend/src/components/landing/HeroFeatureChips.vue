<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

const chips: Array<{ title: string; pos: string; anim: string; icon: VtIconName }> = [
  { title: "Cek kata", pos: "left-[0%] top-[36px] -rotate-3", anim: "animate-float-a", icon: "text-match" },
  { title: "Cek makna", pos: "left-[4%] top-[200px] rotate-3", anim: "animate-float-b", icon: "meaning" },
  { title: "Teks AI", pos: "right-[0%] top-[32px] rotate-3", anim: "animate-float-b", icon: "stylometric" },
  { title: "Parafrase", pos: "right-[4%] top-[196px] -rotate-3", anim: "animate-float-a", icon: "rewrite" },
];
</script>

<template>
  <div class="pointer-events-none hidden xl:block" aria-hidden="true">
    <div
      v-for="c in chips"
      :key="c.title"
      class="pointer-events-auto absolute flex w-max items-center gap-2.5 whitespace-nowrap rounded-full bg-white px-4 py-2.5 shadow-lift transition-all duration-300 hover:scale-105 hover:shadow-float cursor-default"
      :class="[c.pos, c.anim]"
    >
      <VtIcon :name="c.icon" tone="current" class="h-[18px] w-[18px] shrink-0 text-[#0F766E]" />
      <span class="text-[12.5px] font-semibold text-[#14111C]">{{ c.title }}</span>
    </div>
  </div>
</template>
