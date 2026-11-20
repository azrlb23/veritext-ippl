<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

const tiles: Array<{ icon: VtIconName; color: string; offset: string }> = [
  { icon: "text-match", color: "text-[#0F766E]", offset: "translate-y-2 -rotate-12" },
  { icon: "meaning", color: "text-[#14111C]", offset: "-translate-y-1 -rotate-6" },
  { icon: "stylometric", color: "text-[#D97706]", offset: "translate-y-2.5 rotate-0" },
  { icon: "rewrite", color: "text-[#0F766E]", offset: "-translate-y-1 rotate-6" },
  { icon: "verified", color: "text-[#14111C]", offset: "translate-y-2 rotate-12" },
];
</script>

<template>
  <div class="flex items-center justify-center gap-3.5 sm:gap-5" aria-hidden="true">
    <div
      v-for="(t, i) in tiles"
      :key="`${t.icon}-${i}`"
      class="flex h-11 w-11 items-center justify-center rounded-[14px] bg-white shadow-lift transition-transform duration-300 hover:-translate-y-1"
      :class="t.offset"
    >
      <VtIcon :name="t.icon" class="h-5 w-5" :class="t.color" />
    </div>
  </div>
</template>
