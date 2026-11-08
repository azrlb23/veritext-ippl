<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const hoverIdx = ref(0);
const isUserHovering = ref(false);
let timer: ReturnType<typeof setInterval> | null = null;

const rows = [
  { text: "Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.", mark: "bg-[#FEE2E2]", note: "Sumber web 94%", tag: "Mirip sumber web.", detail: "Kalimat cocok 94% dengan artikel publik.", color: "text-[#DC2626]" },
  { text: "Sebagian besar responden menyatakan puas dengan layanan tersebut.", mark: "bg-[#FFEDD5]", note: "Mirip makna 81%", tag: "Parafrasa semantik.", detail: "81% kemiripan struktur makna terdeteksi.", color: "text-[#EA580C]" },
  { text: "Penting untuk dicatat bahwa era digital membawa banyak perubahan.", mark: "bg-[#FEF3C7]", note: "Pola tulisan AI", tag: "Anomali stilometri.", detail: "Keseragaman ritme pola mesin terdeteksi.", color: "text-[#CA8A04]" },
  { text: "Data dikumpulkan melalui wawancara mendalam dengan sepuluh narasumber.", mark: "bg-[#DCFCE7]", note: "Sudah diperbaiki", tag: "Naskah orisinal.", detail: "Telah diperbaiki lewat parafrase in-place.", color: "text-[#16A34A]" },
];

function onEnterRow(idx: number) {
  isUserHovering.value = true;
  hoverIdx.value = idx;
}

function onLeavePanel() {
  isUserHovering.value = false;
}

onMounted(() => {
  timer = setInterval(() => {
    if (!isUserHovering.value) {
      hoverIdx.value = (hoverIdx.value + 1) % rows.length;
    }
  }, 2800);
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<template>
  <div class="relative" aria-hidden="true" @mouseleave="onLeavePanel">
    <div class="absolute -top-6 left-1/2 z-10 -translate-x-1/2 w-[calc(100%-1rem)] rounded-[18px] bg-white px-4 py-2.5 sm:w-auto sm:whitespace-nowrap text-[12.5px] text-[#14111C] shadow-lift flex items-center gap-2.5 transition-all duration-300">
      <svg class="h-4 w-4 shrink-0 transition-colors duration-300" :class="rows[hoverIdx].color" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l9 16H3L12 3zM12 10v4M12 17.5v.01" />
      </svg>
      <span class="transition-all duration-200">
        <strong class="font-semibold">{{ rows[hoverIdx].tag }}</strong> {{ rows[hoverIdx].detail }}
      </span>
    </div>

    <div class="rounded-[30px] bg-white px-4 pb-4 pt-9 shadow-float transition-all duration-300">
      <div class="flex items-center justify-between px-2 pb-3">
        <span class="text-[14px] font-semibold text-[#14111C]">Hasil per kalimat</span>
        <span class="text-[11px] font-medium text-[#6D28D9] bg-[#F3EEFA] px-2.5 py-0.5 rounded-full">Sorot kalimat</span>
      </div>

      <div class="space-y-1">
        <div
          v-for="(r, idx) in rows"
          :key="r.note"
          class="flex items-center justify-between gap-4 rounded-[18px] px-3 py-3 text-left transition-all duration-200 cursor-pointer"
          :class="hoverIdx === idx ? 'bg-[#F3EEFA]/80 scale-[1.01] shadow-sm' : 'even:bg-[#F7F4FB] hover:bg-[#F3EEFA]/40'"
          @mouseenter="onEnterRow(idx)"
        >
          <p class="min-w-0 text-[13px] leading-[1.55] text-[#14111C]">
            <span class="rounded-[6px] px-1 py-0.5 transition-colors" :class="r.mark">{{ r.text }}</span>
          </p>
          <span class="hidden shrink-0 text-[12px] text-[#5E5A6B] sm:block tabular-nums">{{ r.note }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
