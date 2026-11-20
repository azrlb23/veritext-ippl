<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useSectionReveal } from "../../composables";
import PipelineTierCard, { type TierItem } from "./PipelineTierCard.vue";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.12 });
const activeTier = ref<number>(1);
const isHovered = ref(false);
let cycleTimer: ReturnType<typeof setInterval> | null = null;

const tiers: TierItem[] = [
  {
    id: 0,
    shortTitle: "Cocokkan Kata",
    title: "Menemukan Salin-Tempel",
    description:
      "Mencocokkan naskah kalimat demi kalimat dengan dokumen pembanding, bahkan untuk potongan yang sangat pendek.",
    weight: "50% skor",
    icon: "lexical",
  },
  {
    id: 1,
    shortTitle: "Pahami Makna",
    title: "Menangkap Parafrasa",
    description:
      "Mengenali kalimat yang susunan atau sinonimnya diubah, tetapi maknanya tetap sama dengan sumber asli.",
    weight: "35% skor",
    icon: "semantic",
  },
  {
    id: 2,
    shortTitle: "Deteksi Gaya AI",
    title: "Menandai Gaya Janggal",
    description:
      "Melihat perubahan ritme dan kekayaan kata yang khas dari teks buatan AI, bukan tulisan manusia.",
    weight: "15% skor",
    icon: "stylometric",
  },
  {
    id: 3,
    shortTitle: "Skor & Perbaikan",
    title: "Laporan & Parafrase",
    description:
      "Menggabungkan seluruh hasil pemeriksaan menjadi satu skor akhir yang jelas beserta saran parafrase terarah.",
    weight: "Skor akhir",
    icon: "verified",
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
    <div class="mb-12 flex flex-col justify-between gap-8 md:flex-row md:items-end">
      <div class="vt-reveal">
        <h2 class="text-[34px] font-semibold leading-[1.08] tracking-[-0.04em] text-[#14111C] sm:text-[48px]">
          Tiga lapis pemeriksaan,
          <span class="block">satu skor.</span>
        </h2>
      </div>

      <div class="vt-reveal vt-d-1 md:max-w-[340px]">
        <p class="text-[15px] leading-[1.65] text-[#4B4757]">
          Setiap lapis menangkap jenis kemiripan yang berbeda, lalu digabung menjadi satu skor yang bisa ditelusuri.
        </p>
      </div>
    </div>

    <div
      class="vt-reveal vt-d-2 flex flex-col items-stretch gap-4 md:h-[460px] md:flex-row md:items-center lg:gap-5"
      style="contain: layout style;"
    >
      <PipelineTierCard
        v-for="tier in tiers"
        :key="tier.id"
        :tier="tier"
        :is-active="activeTier === tier.id"
        @select="activeTier = tier.id"
      />
    </div>
  </section>
</template>
