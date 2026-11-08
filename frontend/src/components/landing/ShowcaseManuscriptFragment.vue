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

const parts: { text: string; key?: Filter; mark?: string }[] = [
  { text: "Perubahan iklim global merupakan " },
  { text: "tantangan terbesar yang dihadapi umat manusia", key: "lex", mark: "bg-[#FEE2E2]" },
  { text: " pada abad ke-21 karena berdampak langsung pada ketahanan pangan, " },
  { text: "kestabilan ekonomi negara berkembang", key: "sem", mark: "bg-[#FFEDD5]" },
  { text: ". Dalam konteks ini, " },
  { text: "penting dicatat bahwa", key: "sty", mark: "bg-[#FEF3C7]" },
  { text: " mitigasi harus dilakukan secara terkoordinasi." },
];

const legend = [
  { label: "Sama dengan sumber", mark: "bg-[#FEE2E2]" },
  { label: "Mirip makna", mark: "bg-[#FFEDD5]" },
  { label: "Pola tulisan AI", mark: "bg-[#FEF3C7]" },
];

const isOn = (key?: Filter) => key !== undefined && (active.value === "all" || active.value === key);
</script>

<template>
  <div class="flex flex-col lg:col-span-7 rounded-[28px] bg-white p-6 shadow-lift sm:p-8">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <span class="text-[14px] font-semibold text-[#0B0F19]">Fragmen naskah</span>
      <div class="flex items-center gap-1 rounded-full bg-[#F1F4FB] p-1 text-[12px]">
        <button
          v-for="f in filters"
          :key="f.key"
          type="button"
          @click="active = f.key"
          class="cursor-pointer rounded-full px-3 py-1 font-medium transition-colors duration-200"
          :class="active === f.key ? 'bg-[#0B0F19] text-white shadow-sm' : 'text-[#4A5266] hover:text-[#0B0F19]'"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <p class="mt-6 text-[16px] leading-[1.9] text-[#0B0F19]">
      <template v-for="(p, i) in parts" :key="i">
        <span v-if="p.key" class="rounded-[7px] px-1.5 py-0.5 transition-colors duration-200" :class="isOn(p.key) ? p.mark : ''">{{ p.text }}</span>
        <template v-else>{{ p.text }}</template>
      </template>
    </p>

    <div class="mt-auto flex flex-wrap pt-7 items-center gap-x-5 gap-y-2 text-[12.5px] text-[#4A5266]">
      <span v-for="l in legend" :key="l.label" class="flex items-center gap-2">
        <span class="h-3.5 w-6 rounded-[5px]" :class="l.mark"></span>{{ l.label }}
      </span>
    </div>
  </div>
</template>
