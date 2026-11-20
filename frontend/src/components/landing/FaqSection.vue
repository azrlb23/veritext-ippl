<script setup lang="ts">
import { useSectionReveal } from "../../composables";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.12 });

const faqs = [
  {
    num: "01",
    q: "Apakah naskah saya disimpan?",
    a: "Tidak. Naskah tidak pernah masuk ke korpus publik dan dapat dihapus permanen kapan saja sesuai UU PDP.",
  },
  {
    num: "02",
    q: "Bagaimana hitungan biaya token?",
    a: "1 token per 2.500 kata, dengan batas maksimal 5 token per dokumen meski naskah skripsi sangat panjang.",
  },
  {
    num: "03",
    q: "Apa beda Gratis dan Premium?",
    a: "Gratis mendapat 5 token dan 3x trial AI. Premium mendukung naskah panjang, parafrase 3 mode, dan PDF ber-QR.",
  },
  {
    num: "04",
    q: "Apakah akurat untuk bahasa Indonesia?",
    a: "Ya. Kami memadukan pencocokan kata Winnowing, makna IndoBERT, dan analisis gaya bahasa Indonesia.",
  },
  {
    num: "05",
    q: "Bagaimana verifikasi keaslian laporan?",
    a: "Setiap laporan PDF resmi memiliki QR Code unik yang bisa dipindai untuk mengecek keasliannya secara publik.",
  },
];
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section mx-auto max-w-[1180px] select-none px-4 py-14 font-sans sm:px-6 sm:py-20"
    :class="{ 'is-visible': isVisible }"
    aria-label="Pertanyaan yang sering ditanyakan"
  >
    <h2 class="vt-reveal mb-12 text-center text-[32px] font-semibold leading-[1.12] tracking-[-0.04em] text-[#14111C] sm:mb-16 sm:text-[46px]">
      Pertanyaan yang sering
      <span class="vt-accent block">ditanyakan.</span>
    </h2>

    <div class="vt-reveal vt-d-1 relative mx-auto grid max-w-[820px] grid-cols-1 gap-x-10 gap-y-8 md:grid-cols-2">
      <svg
        class="pointer-events-none absolute inset-0 hidden h-full w-full md:block"
        viewBox="0 0 820 620"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M210 95 C410 35, 430 175, 610 155 C720 145, 420 265, 210 305 C80 330, 440 390, 610 375 C710 365, 420 495, 210 530"
          stroke="#D7D0E4"
          stroke-width="1.5"
          stroke-dasharray="6 6"
          stroke-linecap="round"
        />
      </svg>

      <article
        v-for="(item, idx) in faqs"
        :key="item.num"
        class="relative z-10 h-fit rounded-[22px] border border-[#ECE8F4] bg-white p-3.5 shadow-float transition-transform duration-300 hover:rotate-0 hover:-translate-y-1"
        :class="idx % 2 === 0 ? '-rotate-2' : 'rotate-2 md:mt-10'"
      >
        <div
          class="mx-auto -mt-5 mb-2 h-3.5 w-3.5 rounded-full shadow-sm"
          :class="idx % 2 === 0 ? 'bg-[#0F766E]' : 'bg-[#D97706]'"
        />
        <div
          class="rounded-[14px] p-4 text-left"
          :class="idx % 2 === 0 ? 'bg-[#EBF8F6]' : 'bg-[#FAF4EA]'"
        >
          <span
            class="block text-[20px] font-light leading-none"
            :class="idx % 2 === 0 ? 'text-[#0F766E]' : 'text-[#D97706]'"
          >
            {{ item.num }}
          </span>
          <h3 class="mt-2.5 text-[15px] font-semibold leading-[1.35] text-[#14111C]">
            {{ item.q }}
          </h3>
          <p class="mt-1.5 text-[13px] leading-[1.55] text-[#4B4757]">
            {{ item.a }}
          </p>
        </div>
      </article>
    </div>
  </section>
</template>
