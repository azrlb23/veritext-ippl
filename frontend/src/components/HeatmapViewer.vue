<script setup lang="ts">
import { ref, computed } from "vue";
import type { HeatmapAnnotation } from "../types";

const props = defineProps<{
  text?: string | null;
  annotations: HeatmapAnnotation[];
}>();

const emit = defineEmits<{
  (e: "selectAnnotation", anno: HeatmapAnnotation): void;
}>();

const selectedAnnotation = ref<HeatmapAnnotation | null>(null);
const showT1 = ref<boolean>(true);
const showT2 = ref<boolean>(true);
const showT3 = ref<boolean>(true);

function getHighlightClass(tier: string) {
  if (tier === "T1" && showT1.value) return "highlight-t1 cursor-pointer font-medium bg-red-100 text-red-900 px-0.5 rounded transition-colors hover:bg-red-200";
  if (tier === "T2" && showT2.value) return "highlight-t2 cursor-pointer font-medium bg-orange-100 text-orange-900 px-0.5 rounded transition-colors hover:bg-orange-200";
  if (tier === "T3" && showT3.value) return "highlight-t3 cursor-pointer font-medium bg-yellow-100 text-yellow-900 px-0.5 rounded transition-colors hover:bg-yellow-200";
  return "";
}

function selectAnno(anno: HeatmapAnnotation) {
  selectedAnnotation.value = anno;
  emit("selectAnnotation", anno);
}

interface TextSlice {
  text: string;
  annotation?: HeatmapAnnotation;
  isHighlighted: boolean;
}

const renderedSlices = computed<TextSlice[]>(() => {
  const rawText = props.text;
  if (!rawText) return [];
  if (!props.annotations || props.annotations.length === 0) {
    return [{ text: rawText, isHighlighted: false }];
  }

  // Filter annotations by active tier toggle
  const activeAnnos = props.annotations.filter((a) => {
    if (a.tier === "T1") return showT1.value;
    if (a.tier === "T2") return showT2.value;
    if (a.tier === "T3") return showT3.value;
    return true;
  });

  const sorted = [...activeAnnos].sort((a, b) => a.start - b.start);
  const slices: TextSlice[] = [];
  let currentPos = 0;

  for (const anno of sorted) {
    const start = Math.max(0, Math.min(anno.start, rawText.length));
    const end = Math.max(start, Math.min(anno.end, rawText.length));

    // Fill gap before this annotation if needed
    const effectiveStart = Math.max(start, currentPos);
    if (effectiveStart > currentPos) {
      slices.push({
        text: rawText.substring(currentPos, effectiveStart),
        isHighlighted: false,
      });
      currentPos = effectiveStart;
    }

    // Highlight annotation slice (handling potential overlaps without dropping text)
    if (end > currentPos) {
      slices.push({
        text: rawText.substring(currentPos, end),
        annotation: anno,
        isHighlighted: true,
      });
      currentPos = end;
    }
  }

  if (currentPos < rawText.length) {
    slices.push({
      text: rawText.substring(currentPos),
      isHighlighted: false,
    });
  }

  return slices;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Tier Filtering Toggles -->
    <div class="flex flex-wrap items-center justify-between gap-3 p-4 bg-white border border-[#ededed] rounded-[20px] shadow-[0_0_0_1px_rgba(4,23,43,0.05)]">
      <div class="flex items-center space-x-2 text-xs font-medium text-[#17191c] tracking-tight">
        <span>Filter Lapisan Sorotan:</span>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          @click="showT1 = !showT1"
          class="px-3.5 py-1 text-xs font-medium rounded-full border transition-all flex items-center"
          :class="showT1 ? 'bg-red-50 text-red-700 border-red-300 ring-1 ring-red-300' : 'bg-white text-[#777b86] border-[#ededed] hover:border-[#17191c]'"
        >
          <span>Tier 1 Leksikal (Merah)</span>
        </button>

        <button
          type="button"
          @click="showT2 = !showT2"
          class="px-3.5 py-1 text-xs font-medium rounded-full border transition-all flex items-center"
          :class="showT2 ? 'bg-orange-50 text-orange-700 border-orange-300 ring-1 ring-orange-300' : 'bg-white text-[#777b86] border-[#ededed] hover:border-[#17191c]'"
        >
          <span>Tier 2 Semantik (Oranye)</span>
        </button>

        <button
          type="button"
          @click="showT3 = !showT3"
          class="px-3.5 py-1 text-xs font-medium rounded-full border transition-all flex items-center"
          :class="showT3 ? 'bg-yellow-50 text-yellow-800 border-yellow-300 ring-1 ring-yellow-300' : 'bg-white text-[#777b86] border-[#ededed] hover:border-[#17191c]'"
        >
          <span>Tier 3 AI (Kuning)</span>
        </button>
      </div>
    </div>

    <!-- Heatmap Document Text Viewer -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="lg:col-span-2 bg-white border border-[#ededed] rounded-[24px] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] leading-relaxed text-sm text-[#17191c] space-y-4">
        <h3 class="text-sm font-semibold text-[#17191c] uppercase tracking-wide mb-2">
          Naskah Dokumen dengan <span class="italic font-normal text-[#777b86]">Interactive Heatmap</span>
        </h3>

        <!-- Dynamic User Manuscript Text Rendering -->
        <div v-if="text" class="prose max-w-none text-[#515151] whitespace-pre-wrap font-normal leading-[1.8]">
          <template v-for="(slice, sIdx) in renderedSlices" :key="sIdx">
            <span
              v-if="slice.isHighlighted && slice.annotation"
              @click="selectAnno(slice.annotation)"
              :class="getHighlightClass(slice.annotation.tier)"
              :title="`[${slice.annotation.tier}] ${slice.annotation.source_title || 'Sumber Korpus'}`"
            >{{ slice.text }}</span>
            <span v-else>{{ slice.text }}</span>
          </template>
        </div>

        <!-- Fallback if text is not provided or empty -->
        <div v-else-if="annotations.length > 0" class="prose max-w-none text-[#515151] space-y-3 font-normal leading-[1.8]">
          <p v-for="(anno, idx) in annotations" :key="idx">
            <span
              @click="selectAnno(anno)"
              :class="getHighlightClass(anno.tier)"
              :title="`[${anno.tier}] ${anno.source_title || 'Sumber Korpus'}`"
            >
              {{ anno.text_snippet }}
            </span>
          </p>
        </div>

        <div v-else class="text-xs text-[#777b86] py-8 text-center italic">
          Tidak ada teks atau temuan kemiripan yang dapat ditampilkan.
        </div>
      </div>

      <!-- Detail Card on Selected Highlight -->
      <div class="bg-white border border-[#ededed] rounded-[24px] p-6 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] space-y-4">
        <h4 class="text-xs font-semibold uppercase tracking-wide text-[#777b86]">
          Detail Temuan Terpilih
        </h4>

        <div v-if="selectedAnnotation" class="space-y-3.5">
          <div class="flex items-center justify-between">
            <span
              class="px-2.5 py-0.5 text-xs font-medium rounded-full"
              :class="
                selectedAnnotation.tier === 'T1'
                  ? 'bg-red-50 text-red-700 border border-red-200'
                  : selectedAnnotation.tier === 'T2'
                  ? 'bg-orange-50 text-orange-700 border border-orange-200'
                  : 'bg-yellow-50 text-yellow-800 border border-yellow-200'
              "
            >
              {{ selectedAnnotation.tier }}: {{ selectedAnnotation.color }}
            </span>
            <span class="text-sm font-semibold text-[#17191c] tabular-nums">
              Sim: {{ (selectedAnnotation.similarity * 100).toFixed(1) }}%
            </span>
          </div>

          <div>
            <div class="text-[11px] font-medium text-[#777b86] uppercase tracking-tight">Sumber Pembanding</div>
            <div class="text-xs font-medium text-[#17191c] mt-0.5">
              {{ selectedAnnotation.source_title || "Pola Korpus Terdaftar" }}
            </div>
          </div>

          <div>
            <div class="text-[11px] font-medium text-[#777b86] uppercase tracking-tight">Kutipan Teks Sumber</div>
            <div class="text-xs italic bg-[#fafafb] border border-[#ededed] p-3 rounded-[14px] text-[#777b86] mt-1">
              "{{ selectedAnnotation.text_snippet }}"
            </div>
          </div>
        </div>

        <div v-else class="text-center py-10 text-xs text-[#777b86] leading-relaxed font-normal">
          Klik salah satu kalimat berwarna pada naskah untuk melihat perbandingan sumber dan skor kemiripan rincian.
        </div>
      </div>
    </div>
  </div>
</template>
