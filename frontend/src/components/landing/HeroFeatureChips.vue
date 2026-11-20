<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

type ChipTarget = "sentence" | "report" | "paraphrase";

const emit = defineEmits<{ (e: "select", target: ChipTarget): void }>();

const chips: Array<{
  title: string;
  sub: string;
  pos: string;
  anim: string;
  icon: VtIconName;
  iconColor: string;
  target: ChipTarget;
}> = [
  { title: "Cek kata", sub: "Kecocokan persis", pos: "left-[0%] top-[28px] -rotate-3", anim: "animate-float-a", icon: "text-match", iconColor: "text-[#0F766E]", target: "sentence" },
  { title: "Cek makna", sub: "Parafrasa terdeteksi", pos: "left-[5%] top-[196px] rotate-2", anim: "animate-float-b", icon: "meaning", iconColor: "text-[#0F766E]", target: "sentence" },
  { title: "Teks AI", sub: "Pola tulisan mesin", pos: "right-[0%] top-[24px] rotate-3", anim: "animate-float-b", icon: "stylometric", iconColor: "text-[#F59E0B]", target: "report" },
  { title: "Parafrase", sub: "Tiga gaya penulisan", pos: "right-[5%] top-[192px] -rotate-2", anim: "animate-float-a", icon: "rewrite", iconColor: "text-[#0F766E]", target: "paraphrase" },
];
</script>

<template>
  <div class="pointer-events-none hidden xl:block">
    <svg
      class="pointer-events-none absolute inset-x-0 top-0 h-[270px] w-full"
      viewBox="0 0 1320 270"
      fill="none"
      aria-hidden="true"
    >
      <path d="M660 40 Q380 26 116 56" stroke="#0F766E" stroke-opacity="0.18" stroke-width="1.25" stroke-dasharray="2 7" />
      <path d="M660 52 Q385 118 164 218" stroke="#0F766E" stroke-opacity="0.18" stroke-width="1.25" stroke-dasharray="2 7" />
      <path d="M660 40 Q940 24 1204 52" stroke="#0F766E" stroke-opacity="0.18" stroke-width="1.25" stroke-dasharray="2 7" />
      <path d="M660 52 Q935 116 1156 214" stroke="#0F766E" stroke-opacity="0.18" stroke-width="1.25" stroke-dasharray="2 7" />
    </svg>

    <button
      v-for="c in chips"
      :key="c.title"
      type="button"
      class="pointer-events-auto absolute flex w-max cursor-pointer items-center gap-3 whitespace-nowrap rounded-[18px] border border-[#E4EEEC] bg-white px-3.5 py-2.5 text-left shadow-lift transition-[transform,box-shadow,border-color] duration-200 hover:-translate-y-1 hover:scale-[1.03] hover:border-[#CBE6E1] hover:shadow-float"
      :class="[c.pos, c.anim]"
      @click="emit('select', c.target)"
    >
      <VtIcon :name="c.icon" tone="current" class="h-5 w-5 shrink-0" :class="c.iconColor" />
      <span>
        <span class="block text-[12.5px] font-semibold text-[#14111C]">{{ c.title }}</span>
        <span class="block text-[10.5px] text-[#5E5A6B]">{{ c.sub }}</span>
      </span>
    </button>
  </div>
</template>
