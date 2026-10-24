<script setup lang="ts">
import { ref, computed } from "vue";
import type { HeatmapAnnotation } from "../../types";
import Badge from "../common/Badge.vue";
import EmptyState from "../common/EmptyState.vue";

interface Props {
  annotations: HeatmapAnnotation[];
  documentText?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  annotations: () => [],
  documentText: null,
});

const emit = defineEmits<{
  (e: "selectAnnotation", anno: HeatmapAnnotation): void;
}>();

const selectedIndex = ref<number>(0);

const safeIndex = computed<number>(() => {
  if (props.annotations.length === 0) return 0;
  return Math.min(Math.max(0, selectedIndex.value), props.annotations.length - 1);
});

const currentAnnotation = computed<HeatmapAnnotation | null>(() => {
  return props.annotations[safeIndex.value] || null;
});

function selectItem(idx: number) {
  selectedIndex.value = idx;
  if (props.annotations[idx]) {
    emit("selectAnnotation", props.annotations[idx]);
  }
}

const currentSentenceText = computed<string>(() => {
  const currentAnno = currentAnnotation.value;
  if (!currentAnno) return "";
  if (props.documentText && currentAnno.start !== undefined && currentAnno.end !== undefined) {
    const raw = props.documentText.substring(currentAnno.start, currentAnno.end).trim();
    if (raw) return raw;
  }
  return currentAnno.text_snippet || "Kutipan kalimat naskah asli pengguna.";
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6 space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#ededed] pb-4">
      <div>
        <h3 class="text-sm font-extrabold uppercase tracking-wide text-[#262626]">
          Komparasi Berdampingan (Side-by-Side Diff)
        </h3>
        <p class="text-xs text-[#737373] mt-0.5">
          Perbandingan kalimat naskah dengan segmen kutipan korpus yang <span class="italic font-bold text-[#262626]">terdeteksi kemiripan</span>
        </p>
      </div>

      <div v-if="annotations.length > 0" class="flex items-center space-x-1">
        <button
          v-for="(_, idx) in annotations"
          :key="idx"
          @click="selectItem(idx)"
          class="w-7 h-7 rounded-[4px] text-xs font-bold tabular-nums transition-all"
          :class="safeIndex === idx ? 'bg-[#262626] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)]' : 'bg-[#fafafa] hover:bg-[#ededed] text-[#515151] border border-[#ededed]'"
        >
          #{{ idx + 1 }}
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="annotations.length === 0" class="py-6">
      <EmptyState
        title="Tidak Ada Temuan Kemiripan"
        description="Tidak ditemukan segmen naskah yang memerlukan perbandingan berdampingan."
      />
    </div>

    <!-- Comparison View -->
    <div v-else-if="currentAnnotation" class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <Badge
            :variant="currentAnnotation.tier === 'T1' ? 'danger' : currentAnnotation.tier === 'T2' ? 'warning' : 'neutral'"
            size="sm"
          >
            {{ currentAnnotation.tier }} &bull; {{ currentAnnotation.color }}
          </Badge>
          <span class="text-xs font-medium text-[#515151]">
            Sumber: <strong class="text-[#262626] font-bold">{{ currentAnnotation.source_title || 'Bank Korpus' }}</strong>
          </span>
        </div>

        <div class="text-xs font-extrabold tabular-nums px-2.5 py-1 rounded-full bg-[#ededed] text-[#262626] border border-[#ededed]">
          Skor: {{ (currentAnnotation.similarity * 100).toFixed(1) }}%
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Original Document Sentence -->
        <div class="border border-[#ededed] rounded-[8px] p-4 bg-[#fafafa] space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">
              Naskah yang Diuji
            </span>
            <span class="text-[10px] tabular-nums font-medium text-[#929292]">
              Offset {{ currentAnnotation.start }}-{{ currentAnnotation.end }}
            </span>
          </div>
          <p class="text-xs text-[#262626] leading-relaxed font-normal bg-white p-3 rounded-[4px] border border-[#ededed]">
            {{ currentSentenceText }}
          </p>
        </div>

        <!-- Matched Corpus Source -->
        <div class="border border-[#ededed] rounded-[8px] p-4 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">
              Koleksi Sumber Pembanding
            </span>
            <span class="text-[10px] italic font-bold text-[#737373]">
              HNSW Cosine Match
            </span>
          </div>
          <p class="text-xs text-[#262626] leading-relaxed font-normal bg-[#fafafa] p-3 rounded-[4px] border border-[#ededed]">
            "{{ currentAnnotation.text_snippet }}"
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
