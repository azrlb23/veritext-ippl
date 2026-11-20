<script setup lang="ts">
import { ref } from "vue";
import { useSectionReveal } from "../../composables";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.12 });
const openIndex = ref<number | null>(0);

const faqs = [
  {
    q: "Apakah naskah saya disimpan ke database publik?",
    a: "Tidak. Naskah tidak pernah dimasukkan ke korpus publik dan dapat dihapus permanen kapan saja sesuai UU PDP.",
  },
  {
    q: "Bagaimana cara menghitung biaya token?",
    a: "Biaya pemeriksaan adalah 1 token per 2.500 kata, dengan batas maksimal 5 token per dokumen meski naskah sangat panjang.",
  },
  {
    q: "Apa bedanya akun Gratis dan Premium?",
    a: "Akun Gratis mendapat 5 token dan 3x trial AI. Premium mendukung naskah panjang, parafrase 3 mode, dan unduh PDF ber-QR.",
  },
  {
    q: "Apakah deteksi AI akurat untuk bahasa Indonesia?",
    a: "Ya. Sistem memadukan pencocokan kata Winnowing, makna IndoBERT, serta analisis gaya bahasa khusus bahasa Indonesia.",
  },
  {
    q: "Bagaimana cara memverifikasi keaslian laporan?",
    a: "Setiap laporan PDF resmi dilengkapi QR Code unik yang dapat dipindai untuk mengecek keasliannya secara publik.",
  },
];

function toggle(idx: number) {
  openIndex.value = openIndex.value === idx ? null : idx;
}
</script>

<template>
  <section
    ref="sectionRef"
    class="vt-section mx-auto max-w-[1180px] select-none px-4 py-16 font-sans sm:px-6 sm:py-24"
    :class="{ 'is-visible': isVisible }"
    aria-label="Pertanyaan yang sering diajukan"
  >
    <div class="grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
      <div class="vt-reveal lg:col-span-5">
        <h2 class="text-[32px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#14111C] sm:text-[42px]">
          Pertanyaan yang
          <span class="block">sering diajukan</span>
        </h2>
        <p class="mt-4 max-w-sm text-[15px] leading-[1.65] text-[#5E5A6B]">
          Temukan jawaban cepat seputar pemeriksaan naskah, privasi dokumen, dan penggunaan token di VeriText AI.
        </p>
      </div>

      <div class="vt-reveal vt-d-1 space-y-3 lg:col-span-7">
        <div
          v-for="(item, idx) in faqs"
          :key="item.q"
          class="rounded-[20px] border bg-white transition-[border-color,box-shadow] duration-300 ease-out"
          :class="openIndex === idx
            ? 'border-[#D5ECE8] shadow-[0_20px_48px_-18px_rgba(15,118,110,0.16)]'
            : 'border-[#E8ECEB] shadow-[0_10px_28px_-16px_rgba(20,17,28,0.08)] hover:border-[#CBE6E1]'"
          @mouseenter="openIndex = idx"
        >
          <button
            type="button"
            class="flex w-full cursor-pointer items-center justify-between gap-4 px-5 py-4 text-left"
            :aria-expanded="openIndex === idx"
            @click="toggle(idx)"
          >
            <span class="text-[15px] font-medium text-[#14111C]">{{ item.q }}</span>
            <svg
              class="h-4 w-4 shrink-0 text-[#0F766E] transition-transform duration-300 ease-out"
              :class="openIndex === idx ? 'rotate-45' : ''"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 5v14M5 12h14" />
            </svg>
          </button>
          <div
            class="grid transition-[grid-template-rows,opacity] duration-300 ease-out"
            :class="openIndex === idx ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
          >
            <div class="overflow-hidden">
              <div class="px-5 pb-4 text-[14px] leading-[1.6] text-[#4B4757]">
                {{ item.a }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
