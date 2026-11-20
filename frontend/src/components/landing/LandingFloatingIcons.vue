<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

const icons: Array<{ icon: VtIconName; cls: string }> = [
  { icon: "lexical", cls: "left-[3%] top-[32%] h-11 w-11 rounded-[14px] -rotate-12 animate-float-a text-[#0F766E]" },
  { icon: "rewrite", cls: "right-[4%] top-[39%] h-10 w-10 rounded-[13px] rotate-12 animate-float-b text-[#14111C]" },
  { icon: "stylometric", cls: "left-[6%] top-[49%] h-9 w-9 rounded-[12px] rotate-6 animate-float-b text-[#D97706]" },
  { icon: "semantic", cls: "right-[2%] top-[58%] h-12 w-12 rounded-[15px] -rotate-6 animate-float-a text-[#0F766E]" },
  { icon: "verified", cls: "left-[2%] top-[69%] h-10 w-10 rounded-[13px] -rotate-12 animate-float-a text-[#14111C]" },
  { icon: "text-match", cls: "right-[6%] top-[76%] h-11 w-11 rounded-[14px] rotate-6 animate-float-b text-[#0F766E]" },
  { icon: "meaning", cls: "left-[5%] top-[88%] h-10 w-10 rounded-[13px] rotate-12 animate-float-a text-[#D97706]" },
];
</script>

<template>
  <div
    v-for="(item, i) in icons"
    :key="`${item.icon}-${i}`"
    class="pointer-events-none absolute hidden items-center justify-center bg-white shadow-lift lg:flex"
    :class="item.cls"
  >
    <VtIcon :name="item.icon" tone="current" class="h-[18px] w-[18px]" />
  </div>
</template>
