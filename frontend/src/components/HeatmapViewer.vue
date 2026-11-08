<script setup lang="ts">
import { ref, computed } from "vue";
import type { HeatmapAnnotation } from "../types";

const props = defineProps<{
  text?: string | null;
  annotations: HeatmapAnnotation[];
  selectedAnnotation?: HeatmapAnnotation | null;
}>();

const emit = defineEmits<{
  (e: "select-annotation", anno: HeatmapAnnotation): void;
  (e: "select-sentence", anno: HeatmapAnnotation): void;
  (e: "selectAnnotation", anno: HeatmapAnnotation): void;
}>();

const activeLayers = ref<Record<string, boolean>>({ T1: true, T2: true, T3: true, RESOLVED: true });

function getHighlightClass(anno: HeatmapAnnotation) {
  const isSelected = props.selectedAnnotation && (
    props.selectedAnnotation.sentence_id === anno.sentence_id ||
    (props.selectedAnnotation.start === anno.start && props.selectedAnnotation.end === anno.end)
  );
  const ring = isSelected ? " ring-2 ring-[#1560BD] ring-offset-1 font-semibold" : "";
  if ((anno.color === "RESOLVED_GREEN" || (anno as any).match_type === "RESOLVED_GREEN") && activeLayers.value.RESOLVED) {
    return `bg-[#DCFCE7] text-[#166534] border-b-2 border-[#22C55E] cursor-pointer px-0.5 rounded hover:bg-green-100${ring}`;
  }
  if ((anno.color === "RED" || anno.tier === "T1") && activeLayers.value.T1) {
    return `bg-red-100 text-red-900 border-b-2 border-red-500 cursor-pointer px-0.5 rounded hover:bg-red-200${ring}`;
  }
  if ((anno.color === "ORANGE" || anno.tier === "T2") && activeLayers.value.T2) {
    return `bg-orange-100 text-orange-900 border-b-2 border-orange-500 cursor-pointer px-0.5 rounded hover:bg-orange-200${ring}`;
  }
  if ((anno.color === "YELLOW" || anno.tier === "T3") && activeLayers.value.T3) {
    return `bg-yellow-100 text-yellow-900 border-b-2 border-yellow-400 cursor-pointer px-0.5 rounded hover:bg-yellow-200${ring}`;
  }
  return "";
}

function onSelect(anno: HeatmapAnnotation) {
  emit("select-annotation", anno);
  emit("select-sentence", anno);
  emit("selectAnnotation", anno);
}

const renderedSlices = computed(() => {
  const rawText = props.text;
  if (!rawText) return [];
  if (!props.annotations || props.annotations.length === 0) return [{ text: rawText, isHighlighted: false }];
  const sorted = [...props.annotations].sort((a, b) => a.start - b.start);
  const slices = [];
  let pos = 0;
  for (const anno of sorted) {
    const s = Math.max(0, Math.min(anno.start, rawText.length));
    const e = Math.max(s, Math.min(anno.end, rawText.length));
    if (s > pos) slices.push({ text: rawText.substring(pos, s), isHighlighted: false });
    if (e > pos) {
      slices.push({ text: rawText.substring(pos, e), annotation: anno, isHighlighted: true });
      pos = e;
    }
  }
  if (pos < rawText.length) slices.push({ text: rawText.substring(pos), isHighlighted: false });
  return slices;
});

const filterTabs = [
  { key: "T1", label: "Leksikal (Merah)", activeCls: "bg-red-50 text-red-700 border-red-300 ring-1 ring-red-200" },
  { key: "T2", label: "Semantik (Oranye)", activeCls: "bg-orange-50 text-orange-700 border-orange-300 ring-1 ring-orange-200" },
  { key: "T3", label: "Stilometri (Kuning)", activeCls: "bg-yellow-50 text-yellow-800 border-yellow-300 ring-1 ring-yellow-200" },
  { key: "RESOLVED", label: "Hasil Parafrase (Hijau)", activeCls: "bg-green-50 text-green-700 border-green-300 ring-1 ring-green-200" },
];
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2 p-3 bg-white border border-[#E4E8F0] rounded-2xl shadow-sm text-xs">
      <span class="font-medium text-[#4B5563]">Filter Sorotan:</span>
      <div class="flex flex-wrap items-center gap-1.5">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          type="button"
          @click="activeLayers[tab.key] = !activeLayers[tab.key]"
          class="px-2.5 py-1 rounded-full border transition-all text-xs font-medium"
          :class="activeLayers[tab.key] ? tab.activeCls : 'bg-white text-gray-500 border-gray-200'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="bg-white border border-[#E4E8F0] rounded-2xl p-6 sm:p-8 shadow-sm text-sm text-[#1F2937] leading-[1.8] min-h-[480px] max-h-[700px] overflow-y-auto">
      <div v-if="text" class="whitespace-pre-wrap font-serif">
        <template v-for="(slice, sIdx) in renderedSlices" :key="sIdx">
          <span
            v-if="slice.isHighlighted && slice.annotation"
            @click="onSelect(slice.annotation)"
            :class="getHighlightClass(slice.annotation)"
            :title="slice.annotation.source_title ? `Sumber: ${slice.annotation.source_title}` : 'Kalimat tersorot'"
          >{{ slice.text }}</span>
          <span v-else>{{ slice.text }}</span>
        </template>
      </div>
      <div v-else-if="annotations.length > 0" class="space-y-3 font-serif">
        <p v-for="(anno, idx) in annotations" :key="idx">
          <span @click="onSelect(anno)" :class="getHighlightClass(anno)" :title="anno.source_title || 'Kalimat tersorot'">
            {{ anno.text_snippet || 'Cuplikan kalimat' }}
          </span>
        </p>
      </div>
      <div v-else class="text-xs text-gray-400 py-16 text-center italic">
        Tidak ada teks naskah atau temuan kemiripan untuk ditampilkan.
      </div>
    </div>
  </div>
</template>
