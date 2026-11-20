<script setup lang="ts">
interface BubbleItem {
  initial: string;
  name: string;
  quote: string;
  wrapClass: string;
  bubbleClass: string;
}

const bubbles: BubbleItem[] = [
  { initial: "R", name: "Raka", quote: "Skripsi sudah jadi, tapi takut skor kemiripannya tinggi pas dicek kampus.", wrapClass: "flex", bubbleClass: "-rotate-2 bg-[#0F766E] text-white" },
  { initial: "N", name: "Nadia", quote: "Sudah coba parafrase manual berkali-kali, tapi kalimatnya malah jadi aneh dan kaku.", wrapClass: "flex md:flex-row-reverse md:mt-6", bubbleClass: "rotate-2 bg-[#0D9488] text-white" },
  { initial: "D", name: "Dimas", quote: "Bingung kalimat mana yang kena deteksi AI dan mana yang perlu diperbaiki dulu.", wrapClass: "flex md:ml-10", bubbleClass: "rotate-1 bg-[#0D9488] text-white" },
  { initial: "S", name: "Sinta", quote: "Takut naskah disimpan ke database publik kalau cek di situs sembarangan.", wrapClass: "flex md:flex-row-reverse md:mr-8", bubbleClass: "-rotate-2 bg-[#0F766E] text-white" },
  { initial: "B", name: "Bagas", quote: "Butuh laporan yang jelas per kalimat untuk bahan bimbingan dengan dosen.", wrapClass: "hidden md:flex md:ml-4 opacity-70", bubbleClass: "-rotate-2 bg-[#14B8A6] text-white" },
  { initial: "P", name: "Putri", quote: "Ingin asisten yang bantu merapikan kalimat tanpa mengubah makna asli riset.", wrapClass: "hidden md:flex md:flex-row-reverse md:mt-4 opacity-65", bubbleClass: "rotate-2 bg-[#14B8A6] text-white" },
];
</script>

<template>
  <div class="cta-bubble-fade">
    <div class="mx-auto grid max-w-[920px] grid-cols-1 items-start gap-x-8 gap-y-5 md:grid-cols-2">
      <div
        v-for="item in bubbles"
        :key="item.name"
        class="items-start gap-3"
        :class="item.wrapClass"
      >
        <div class="flex shrink-0 flex-col items-center">
          <span
            class="flex h-8 w-8 items-center justify-center rounded-full border border-[#DFD8CA] bg-[#F5EFE6] text-[12px] font-semibold text-[#0F766E]"
            aria-hidden="true"
          >
            {{ item.initial }}
          </span>
          <span class="mt-1 text-[11px] font-medium text-[#5E5A6B]">{{ item.name }}</span>
        </div>
        <p
          class="rounded-2xl px-4 py-3 text-left text-[13.5px] leading-[1.5] shadow-sm transition-transform duration-200 hover:rotate-0 hover:-translate-y-0.5"
          :class="item.bubbleClass"
        >
          {{ item.quote }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media (min-width: 768px) {
  .cta-bubble-fade {
    -webkit-mask-image: linear-gradient(180deg, #000 0%, #000 64%, transparent 100%);
    mask-image: linear-gradient(180deg, #000 0%, #000 64%, transparent 100%);
  }
}
</style>
