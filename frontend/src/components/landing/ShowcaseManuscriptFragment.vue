<script setup lang="ts">
import { ref, watch } from "vue";

type Filter = "all" | "lex" | "sem" | "sty";
const props = defineProps<{ externalFilter?: Filter }>();
const emit = defineEmits<{ (e: "update:filter", key: Filter): void }>();

const active = ref<Filter>(props.externalFilter || "all");
watch(() => props.externalFilter, (k) => { if (k) active.value = k; });

function setFilter(k: Filter) {
  active.value = k;
  emit("update:filter", k);
}

const hoveredTag = ref<number | null>(null);

const filters: { key: Filter; label: string }[] = [
  { key: "all", label: "Semua" },
  { key: "lex", label: "Kata" },
  { key: "sem", label: "Makna" },
  { key: "sty", label: "Pola AI" },
];

const parts = [
  { text: "Perubahan iklim global merupakan " },
  { text: "tantangan terbesar yang dihadapi umat manusia", key: "lex" as Filter, mark: "bg-[#FEE2E2]", n: 1, tip: "Arsip 2023 - 94% identik" },
  { text: " pada abad ke-21 karena berdampak langsung pada ketahanan pangan, " },
  { text: "kestabilan ekonomi negara berkembang", key: "sem" as Filter, mark: "bg-[#FFEDD5]", n: 2, tip: "Parafrasa - 81% semantik" },
  { text: ". Dalam konteks ini, " },
  { text: "penting dicatat bahwa", key: "sty" as Filter, mark: "bg-[#FEF3C7]", n: 3, tip: "Pola mesin - Indeks AI 0.92" },
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
  <div class="rounded-[36px] bg-white p-7 shadow-float sm:p-10 lg:pb-24 transition-all duration-300">
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[14px] font-semibold text-[#14111C]">Naskah-Laporan-2026.pdf</div>
        <div class="text-[12px] text-[#5E5A6B]">Fragmen naskah. Contoh tampilan interaktif.</div>
      </div>
      <div v-if="hoveredTag" class="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-[#14111C] px-3 py-1 text-[11px] font-medium text-white shadow-sm transition-all duration-200">
        {{ parts.find(p => p.n === hoveredTag)?.tip }}
      </div>
    </div>

    <div class="mt-6 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
      <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-[12.5px] text-[#4B4757]">
        <span
          v-for="l in legend"
          :key="l.n"
          class="flex items-center gap-2 cursor-pointer transition-transform hover:scale-105"
          @mouseenter="hoveredTag = l.n"
          @mouseleave="hoveredTag = null"
        >
          <span class="flex h-[18px] w-[18px] items-center justify-center rounded-full bg-[#14111C] text-[10px] font-semibold text-white">{{ l.n }}</span>
          {{ l.label }}
        </span>
      </div>
      <div class="flex items-center gap-1 rounded-full bg-[#F3EEFA] p-1 text-[12px]">
        <button
          v-for="f in filters"
          :key="f.key"
          type="button"
          @click="setFilter(f.key)"
          class="cursor-pointer rounded-full px-3.5 py-1.5 font-medium transition-all duration-200 sm:px-3 sm:py-1"
          :class="active === f.key ? 'bg-[#14111C] text-white shadow-sm scale-105' : 'text-[#4B4757] hover:text-[#14111C]'"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <p class="mt-6 text-[19px] leading-[2.05] tracking-[-0.02em] text-[#14111C] sm:text-[21px]">
      <template v-for="(p, i) in parts" :key="i">
        <span
          v-if="p.key"
          class="rounded-[8px] px-1.5 py-0.5 transition-all duration-200 cursor-pointer"
          :class="[
            isOn(p.key) ? p.mark : 'opacity-40',
            hoveredTag === p.n ? 'ring-2 ring-[#8A3FE0] scale-105 shadow-sm' : ''
          ]"
          @mouseenter="hoveredTag = p.n ?? null"
          @mouseleave="hoveredTag = null"
        >
          {{ p.text }}<sup v-if="isOn(p.key)" class="ml-1 rounded-full bg-[#14111C] px-1.5 py-0.5 text-[10px] font-semibold text-white">{{ p.n }}</sup>
        </span>
        <template v-else>{{ p.text }}</template>
      </template>
    </p>
  </div>
</template>
