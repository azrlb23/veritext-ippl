<script setup lang="ts">
import { ref } from "vue";

type Filter = "all" | "lex" | "sem" | "sty";
const active = ref<Filter>("all");

const filters: { key: Filter; label: string }[] = [
  { key: "all", label: "Semua" },
  { key: "lex", label: "Kata" },
  { key: "sem", label: "Makna" },
  { key: "sty", label: "Pola AI" },
];

const parts: { text: string; key?: Filter; mark?: string; n?: number }[] = [
  { text: "Perubahan iklim global merupakan " },
  { text: "tantangan terbesar yang dihadapi umat manusia", key: "lex", mark: "bg-[#FEE2E2]", n: 1 },
  { text: " pada abad ke-21 karena berdampak langsung pada ketahanan pangan, " },
  { text: "kestabilan ekonomi negara berkembang", key: "sem", mark: "bg-[#FFEDD5]", n: 2 },
  { text: ". Dalam konteks ini, " },
  { text: "penting dicatat bahwa", key: "sty", mark: "bg-[#FEF3C7]", n: 3 },
  { text: " mitigasi harus dilakukan secara terkoordinasi." },
];

const legend = [
  { n: 1, label: "Sama dengan sumber" },
  { n: 2, label: "Mirip makna" },
  { n: 3, label: "Pola tulisan AI" },
];

const isOn = (key?: Filter) => key !== undefined && (active.value === "all" || active.value === key);
</script>

<template>
  <div class="rounded-[36px] bg-white p-7 shadow-float sm:p-10 lg:pb-24">
    <div>
      <div class="text-[14px] font-semibold text-[#14111C]">Naskah-Laporan-2026.pdf</div>
      <div class="text-[12px] text-[#5E5A6B]">Fragmen naskah. Contoh tampilan.</div>
    </div>

    <div class="mt-6 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
      <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-[12.5px] text-[#4B4757]">
        <span v-for="l in legend" :key="l.n" class="flex items-center gap-2">
          <span class="flex h-[18px] w-[18px] items-center justify-center rounded-full bg-[#14111C] text-[10px] font-semibold text-white">{{ l.n }}</span>{{ l.label }}
        </span>
      </div>
      <div class="flex items-center gap-1 rounded-full bg-[#F3EEFA] p-1 text-[12px]">
        <button
          v-for="f in filters"
          :key="f.key"
          type="button"
          @click="active = f.key"
          class="cursor-pointer rounded-full px-3.5 py-3 font-medium transition-colors duration-200 sm:px-3 sm:py-1"
          :class="active === f.key ? 'bg-[#14111C] text-white shadow-sm' : 'text-[#4B4757] hover:text-[#14111C]'"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <p class="mt-6 text-[19px] leading-[2.05] tracking-[-0.02em] text-[#14111C] sm:text-[21px]">
      <template v-for="(p, i) in parts" :key="i">
        <span v-if="p.key" class="rounded-[8px] px-1.5 py-0.5 transition-colors duration-200" :class="isOn(p.key) ? p.mark : ''">
          {{ p.text }}<sup v-if="isOn(p.key)" class="ml-1 rounded-full bg-[#14111C] px-1.5 py-0.5 text-[10px] font-semibold text-white">{{ p.n }}</sup>
        </span>
        <template v-else>{{ p.text }}</template>
      </template>
    </p>
  </div>
</template>
