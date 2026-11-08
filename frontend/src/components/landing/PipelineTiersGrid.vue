<script setup lang="ts">
import { ref } from "vue";
import PipelineTierCard from "./PipelineTierCard.vue";

const activeTier = ref<number>(1);

const tiers = [
  {
    id: 0,
    tabLabel: "Kata",
    title: "Menemukan salin-tempel",
    description: "Mencocokkan naskah kalimat demi kalimat dengan dokumen pembanding, bahkan untuk potongan yang sangat pendek.",
    weight: "50%",
    icon: "doc",
  },
  {
    id: 1,
    tabLabel: "Makna",
    title: "Menangkap parafrasa",
    description: "Mengenali kalimat yang susunan atau sinonimnya diubah, tetapi maknanya tetap sama dengan sumber asli.",
    weight: "35%",
    icon: "stack",
  },
  {
    id: 2,
    tabLabel: "Gaya tulisan",
    title: "Menandai gaya yang janggal",
    description: "Melihat perubahan ritme dan kekayaan kata yang khas dari teks buatan AI, bukan tulisan manusia.",
    weight: "15%",
    icon: "gauge",
  },
];
</script>

<template>
  <section class="mx-auto max-w-[1180px] select-none px-4 py-16 font-sans sm:px-6 sm:py-24" aria-label="Cara kerja tiga lapis pemeriksaan">
    <div class="mx-auto mb-12 max-w-2xl text-center">
      <p class="text-[14px] font-medium text-[#6B7385]">Cara kerja</p>
      <h2 class="mt-3 text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#0B0F19] sm:text-[52px]">
        Tiga lapis pemeriksaan, <span class="vt-accent">satu skor.</span>
      </h2>
      <p class="mx-auto mt-5 max-w-xl text-[16px] leading-[1.65] text-[#4A5266]">
        Setiap lapis menangkap jenis kemiripan yang berbeda, lalu digabung menjadi satu skor yang bisa ditelusuri.
      </p>

      <div class="mt-8 inline-flex items-center gap-1 rounded-full bg-white p-1.5 shadow-lift">
        <button
          v-for="t in tiers"
          :key="t.id"
          type="button"
          @click="activeTier = t.id"
          class="cursor-pointer rounded-full px-5 py-2 text-[13.5px] font-semibold transition-colors duration-200"
          :class="activeTier === t.id ? 'bg-[#0B0F19] text-white' : 'text-[#4A5266] hover:text-[#0B0F19]'"
        >
          {{ t.tabLabel }}
        </button>
      </div>
    </div>

    <div class="vt-stage grid grid-cols-1 items-stretch gap-5 rounded-[40px] p-5 pt-8 sm:p-10 sm:pt-14 md:grid-cols-3 lg:gap-7">
      <PipelineTierCard
        v-for="t in tiers"
        :key="t.id"
        :tier="t"
        :is-active="activeTier === t.id"
        @select="activeTier = t.id"
      />
    </div>

    <p class="mt-10 text-center text-[15px] text-[#4A5266]">
      Skor akhir = 50% kata + 35% makna + 15% gaya tulisan
    </p>
  </section>
</template>
