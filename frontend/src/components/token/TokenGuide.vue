<script setup lang="ts">
import { ref } from "vue";

const isExpanded = ref(false);
const activeTab = ref<"benefits" | "usages">("benefits");

const benefits = [
  { title: "Auto-Upgrade Premium", desc: "Aktif permanen sejak pembelian token pertama." },
  { title: "Naskah hingga 15 MB", desc: "Periksa skripsi penuh tanpa batas 2.500 kata." },
  { title: "Sertifikat PDF ber-QR", desc: "Unduh laporan resmi dengan verifikasi QR publik." },
  { title: "Asisten AI Penuh", desc: "Konsultasi sitasi & parafrase tanpa batas trial." },
];

const usages = [
  { badge: "1 token / 2.500 kata", title: "Pemeriksaan naskah", desc: "Tambahan 1 token tiap 2.500 kata, maksimal 5 token per dokumen." },
  { badge: "1 token / 10 pesan", title: "Asisten AI & parafrase", desc: "Halaman penuh memakai 1 token per 2 halaman." },
  { badge: "Aktif selamanya", title: "Tanpa kedaluwarsa", desc: "Saldo tersimpan dan terpotong saat dipakai." },
];

const toggle = () => (isExpanded.value = !isExpanded.value);
</script>

<template>
  <section
    class="border-b border-[#E6ECEB] pb-4"
    aria-labelledby="token-guide-title"
    @mouseenter="isExpanded = true"
    @mouseleave="isExpanded = false"
  >
    <div class="flex flex-wrap items-center justify-between gap-3 py-1">
      <button
        type="button"
        class="flex flex-1 cursor-pointer items-center justify-between gap-4 text-left focus:outline-none"
        :aria-expanded="isExpanded"
        aria-controls="token-guide-panel"
        @click="toggle"
      >
        <h2 id="token-guide-title" class="text-[16px] font-semibold tracking-[-0.02em] text-[#14111C] sm:text-[17px]">
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
    </div>

    <div
      id="token-guide-panel"
      class="grid transition-[grid-template-rows,opacity] duration-300 ease-out"
      :class="isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
    >
      <div class="overflow-hidden">
        <div class="pt-3">
          <div class="flex gap-6 border-b border-[#E6ECEB]" role="tablist" aria-label="Kategori informasi token">
            <button
              type="button"
              role="tab"
              :aria-selected="activeTab === 'benefits'"
              class="-mb-px cursor-pointer border-b-2 pb-2.5 text-[13.5px] font-semibold transition-colors focus:outline-none"
              :class="activeTab === 'benefits' ? 'border-[#0F766E] text-[#14111C]' : 'border-transparent text-[#5E5A6B] hover:text-[#14111C]'"
              @click.stop="activeTab = 'benefits'"
            >
              Keuntungan Premium
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="activeTab === 'usages'"
              class="-mb-px cursor-pointer border-b-2 pb-2.5 text-[13.5px] font-semibold transition-colors focus:outline-none"
              :class="activeTab === 'usages' ? 'border-[#0F766E] text-[#14111C]' : 'border-transparent text-[#5E5A6B] hover:text-[#14111C]'"
              @click.stop="activeTab = 'usages'"
            >
              Cara Hitung Token
            </button>
          </div>

          <div v-if="activeTab === 'benefits'" class="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div v-for="item in benefits" :key="item.title" class="space-y-1">
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 shrink-0 text-[#0F766E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m5 13 4 4L19 7" />
                </svg>
                <h3 class="text-[14.5px] font-semibold tracking-[-0.01em] text-[#14111C]">{{ item.title }}</h3>
              </div>
              <p class="pl-6 text-[13.5px] leading-relaxed text-[#5E5A6B]">{{ item.desc }}</p>
            </div>
          </div>

          <div v-else class="mt-5 grid gap-5 md:grid-cols-3">
            <div v-for="item in usages" :key="item.title" class="space-y-1">
              <p class="text-[12.5px] font-semibold text-[#0F766E]">{{ item.badge }}</p>
              <h3 class="text-[14.5px] font-semibold tracking-[-0.01em] text-[#14111C]">{{ item.title }}</h3>
              <p class="text-[13.5px] leading-relaxed text-[#5E5A6B]">{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
