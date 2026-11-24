<script setup lang="ts">
import { computed } from "vue";
import type { HeatmapAnnotation } from "../../types";

const props = defineProps<{ selected: HeatmapAnnotation }>();
const pct = (v: number) => (v > 1 ? v : v * 100).toFixed(1).replace(".", ",");
const isAiView = computed(() => props.selected.active_view === "AI" || props.selected.tier === "T3" || props.selected.color === "YELLOW");
</script>

<template>
  <div class="mt-5 space-y-4 border-b border-[#E8ECEB] pb-5">
    <div>
      <p class="text-[13px] font-medium text-[#5E5A6B]">Kalimat terpilih</p>
      <p class="mt-1 text-[15px] leading-relaxed text-[#14111C]">{{ selected.text_snippet || "Kalimat terpilih" }}</p>
    </div>
    <div class="flex items-baseline justify-between gap-4">
      <div class="min-w-0">
        <p class="text-[13px] font-medium text-[#5E5A6B]">{{ isAiView ? "Indikasi Pola Tulisan AI" : "Sumber mirip" }}</p>
        <p class="mt-0.5 text-[14px] font-semibold text-[#14111C]">{{ isAiView ? "Analisis Gaya Penulisan AI" : (selected.source_title || "Sumber pembanding") }}</p>
        <p v-if="isAiView" class="mt-0.5 text-[13.5px] leading-relaxed text-[#4B4757]">{{ selected.ai_reason || selected.reason || "Struktur kalimat seragam atau terindikasi pola penulisan AI." }}</p>
        <p v-else-if="selected.reason" class="mt-0.5 text-[13.5px] leading-relaxed text-[#4B4757]">{{ selected.reason }}</p>
        <p v-if="isAiView && selected.tier !== 'T3' && selected.source_title" class="mt-1.5 text-[12.5px] text-[#5E5A6B]">Juga cocok dengan sumber: {{ selected.source_title }}</p>
        <p v-else-if="!isAiView && selected.ai_flag && selected.ai_reason" class="mt-1.5 text-[12.5px] text-[#5E5A6B]">Juga terindikasi pola AI: {{ selected.ai_reason }}</p>
      </div>
      <p class="flex-shrink-0 text-[24px] font-semibold leading-none tracking-[-0.03em] tabular-nums text-[#14111C]">{{ pct(isAiView ? (selected.ai_score ?? selected.similarity ?? 0) : (selected.similarity ?? 0)) }}%</p>
    </div>
  </div>
</template>
