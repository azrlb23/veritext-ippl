<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

interface FloatingItem {
  id: string;
  icon: VtIconName;
  iconTone: string;
  pos: string;
  anim: string;
  tileClass?: string;
  title?: string;
  sub?: string;
  badge?: string;
  badgeClass?: string;
  dot?: boolean;
}

const items: FloatingItem[] = [
  { id: "word", icon: "text-match", iconTone: "text-[#0F766E]", pos: "left-[0%] top-[22px] -rotate-6", anim: "animate-float-a", title: "Cek kata", sub: "Kecocokan persis", badge: "k=5", badgeClass: "bg-[#E6F7F5] text-[#0F766E]" },
  { id: "tile-meaning", icon: "meaning", iconTone: "text-[#0F766E]", pos: "left-[7%] top-[148px] rotate-3", anim: "animate-float-b", tileClass: "h-11 w-11 rounded-[15px]" },
  { id: "meaning", icon: "verified", iconTone: "text-[#0F766E]", pos: "left-[1%] top-[248px] -rotate-2", anim: "animate-float-a", title: "Cek makna", sub: "Parafrasa", dot: true },
  { id: "ai-text", icon: "stylometric", iconTone: "text-[#D97706]", pos: "right-[5%] top-[16px] rotate-[5deg]", anim: "animate-float-b", title: "Teks AI", sub: "Pola mesin" },
  { id: "paraphrase", icon: "rewrite", iconTone: "text-[#0F766E]", pos: "right-[0%] top-[138px] -rotate-3", anim: "animate-float-a", title: "Parafrase", badge: "3 gaya", badgeClass: "bg-[#FEF3C7] text-[#B45309]" },
  { id: "tile-lexical", icon: "lexical", iconTone: "text-[#D97706]", pos: "right-[7%] top-[256px] rotate-6", anim: "animate-float-b", tileClass: "h-10 w-10 rounded-[14px]" },
];
</script>

<template>
  <div class="pointer-events-none hidden xl:block" aria-hidden="true">
    <div
      v-for="item in items"
      :key="item.id"
      class="pointer-events-auto absolute flex cursor-default items-center justify-center bg-white shadow-lift transition-[transform,box-shadow] duration-300 ease-out hover:-translate-y-1.5 hover:scale-105 hover:shadow-float"
      :class="[item.pos, item.anim, item.tileClass ?? 'w-max gap-3 whitespace-nowrap rounded-[18px] px-3.5 py-2.5']"
    >
      <VtIcon :name="item.icon" tone="current" class="h-5 w-5 shrink-0" :class="item.iconTone" />
      <div v-if="item.title">
        <div class="flex items-center gap-1.5 text-[12.5px] font-semibold text-[#14111C]">
          <span>{{ item.title }}</span>
          <span v-if="item.badge" class="rounded-full px-1.5 py-0.5 text-[10px] font-semibold leading-none" :class="item.badgeClass">{{ item.badge }}</span>
          <span v-if="item.dot" class="h-2 w-2 rounded-full bg-[#14B8A6] animate-pulse" />
        </div>
        <div v-if="item.sub" class="text-[10.5px] text-[#5E5A6B]">{{ item.sub }}</div>
      </div>
    </div>
  </div>
</template>
