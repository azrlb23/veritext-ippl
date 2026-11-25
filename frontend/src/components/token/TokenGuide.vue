<script setup lang="ts">
import { ref } from "vue";

const isExpanded = ref(false);

const usages = [
  {
    title: "Pemeriksaan naskah",
    desc: "1 token untuk naskah hingga 2.500 kata. Naskah panjang dikenai 1 token per kelipatan 2.500 kata, maksimal 5 token per dokumen.",
  },
  {
    title: "Asisten AI & parafrase",
    desc: "1 token untuk 10x sesi konsultasi atau parafrase kalimat/paragraf. Mode parafrase halaman penuh memakai 1 token per 2 halaman.",
  },
  {
    title: "Tanpa masa kedaluwarsa",
    desc: "Token yang sudah dibeli tetap tersimpan di akun Anda dan hanya terpotong saat digunakan.",
  },
];

const benefits = [
  {
    title: "Upgrade otomatis ke Premium",
    desc: "Pembelian token pertama langsung mengaktifkan status Premium tanpa biaya langganan bulanan.",
  },
  {
    title: "Naskah panjang tanpa batas 2.500 kata",
    desc: "Unggah skripsi, tesis, atau jurnal penuh hingga 15 MB.",
  },
  {
    title: "Laporan PDF resmi ber-QR",
    desc: "Unduh sertifikat audit keaslian naskah dengan verifikasi QR publik.",
  },
  {
    title: "Akses penuh Asisten AI",
    desc: "Konsultasi sitasi dan perbaikan kalimat 3-mode tanpa batas kuota trial.",
  },
];

const columns = [
  { heading: "Penggunaan Token", items: usages },
  { heading: "Keuntungan untuk Pengguna", items: benefits },
];

function toggle() {
  isExpanded.value = !isExpanded.value;
}
</script>

<template>
  <section
    class="border-b border-[#E6ECEB] pb-4"
    aria-labelledby="token-guide-title"
    @mouseenter="isExpanded = true"
    @mouseleave="isExpanded = false"
  >
    <button
      type="button"
      class="flex w-full cursor-pointer items-center justify-between gap-4 py-1 text-left focus:outline-none"
      :aria-expanded="isExpanded"
      aria-controls="token-guide-panel"
      @click="toggle"
    >
      <h2
        id="token-guide-title"
        class="text-[16px] font-semibold tracking-[-0.02em] text-[#14111C] sm:text-[17px]"
      >
        Cara pakai dan keuntungan token
      </h2>
      <svg
        class="h-4 w-4 shrink-0 text-[#0F766E] transition-transform duration-300 ease-out"
        :class="isExpanded ? 'rotate-180' : ''"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div
      id="token-guide-panel"
      class="grid transition-[grid-template-rows,opacity] duration-300 ease-out"
      :class="isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
    >
      <div class="overflow-hidden">
        <div class="mt-4 grid gap-8 pt-2 md:grid-cols-2 md:gap-10">
          <div v-for="col in columns" :key="col.heading">
            <h3 class="text-[15px] font-semibold tracking-[-0.015em] text-[#0F766E]">
              {{ col.heading }}
            </h3>
            <ul class="mt-4 space-y-3.5">
              <li v-for="item in col.items" :key="item.title" class="flex items-start gap-3">
                <span class="mt-[9px] h-1.5 w-1.5 shrink-0 rounded-full bg-[#0F766E]" aria-hidden="true" />
                <p class="text-[14px] leading-relaxed text-[#5E5A6B]">
                  <strong class="font-semibold text-[#14111C]">{{ item.title }}:</strong>
                  {{ item.desc }}
                </p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
