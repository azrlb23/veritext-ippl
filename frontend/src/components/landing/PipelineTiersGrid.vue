<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useSectionReveal } from "../../composables";
import PipelineTierCard from "./PipelineTierCard.vue";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.12 });
const activeTier = ref<number>(1);
const isHovered = ref(false);
let cycleTimer: ReturnType<typeof setInterval> | null = null;

const tiers = [
  {
    id: 0,
    tabLabel: "Kata",
    title: "Menemukan salin-tempel",
    description: "Mencocokkan naskah kalimat demi kalimat dengan dokumen pembanding, bahkan untuk potongan yang sangat pendek.",
    weight: "50%",
    icon: "lexical" as const,
  },
  {
    id: 1,
    tabLabel: "Makna",
    title: "Menangkap parafrasa",
    description: "Mengenali kalimat yang susunan atau sinonimnya diubah, tetapi maknanya tetap sama dengan sumber asli.",
    weight: "35%",
    icon: "semantic" as const,
  },
  {
    id: 2,
    tabLabel: "Gaya tulisan",
    title: "Menandai gaya yang janggal",
    description: "Melihat perubahan ritme dan kekayaan kata yang khas dari teks buatan AI, bukan tulisan manusia.",
    weight: "15%",
    icon: "stylometric" as const,
  },
];

onMounted(() => {
  cycleTimer = setInterval(() => {
    if (!isHovered.value) {
      activeTier.value = (activeTier.value + 1) % tiers.length;
    }
  }, 4500);
});

onBeforeUnmount(() => {
  if (cycleTimer) clearInterval(cycleTimer);
});
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section mx-auto max-w-[1180px] select-none px-4 py-16 font-sans sm:px-6 sm:py-24"
    :class="{ 'is-visible': isVisible }"
    aria-label="Cara kerja tiga lapis pemeriksaan"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <div class="mx-auto mb-12 max-w-2xl text-center">
      <p class="vt-reveal text-[14px] font-medium text-[#5E5A6B]">Cara kerja</p>
      <h2 class="vt-reveal vt-d-1 mt-3 text-[34px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#14111C] sm:text-[52px]">
        Tiga lapis pemeriksaan, <span class="vt-accent">satu skor.</span>
      </h2>
      <p class="vt-reveal vt-d-2 mx-auto mt-5 max-w-xl text-[16px] leading-[1.65] text-[#4B4757]">
        Setiap lapis menangkap jenis kemiripan yang berbeda, lalu digabung menjadi satu skor yang bisa ditelusuri.
      </p>

      <div class="vt-reveal vt-d-2 mt-8 inline-flex items-center gap-1 rounded-full bg-white p-1.5 shadow-lift">
        <button
          v-for="t in tiers"
          :key="t.id"
          type="button"
          @click="activeTier = t.id"
          class="cursor-pointer rounded-full px-5 py-2 text-[13.5px] font-semibold transition-all duration-300"
          :class="activeTier === t.id ? 'bg-[#14111C] text-white shadow-sm scale-105' : 'text-[#4B4757] hover:text-[#14111C]'"
        >
          {{ t.tabLabel }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 items-stretch gap-5 pt-4 md:grid-cols-3 lg:gap-7">
      <div
        v-for="(t, idx) in tiers"
        :key="t.id"
        class="flex vt-reveal-zoom"
        :style="{ '--vt-d': `${140 + idx * 100}ms` }"
      >
        <PipelineTierCard
          class="w-full"
          :tier="t"
          :is-active="activeTier === t.id"
          @select="activeTier = t.id"
        />
      </div>
    </div>

    <p class="vt-reveal vt-d-4 mt-10 text-center text-[15px] text-[#4B4757]">
      Skor akhir = 50% kata + 35% makna + 15% gaya tulisan
    </p>
  </section>
</template>
