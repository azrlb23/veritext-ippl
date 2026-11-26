<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { HeatmapAnnotation } from "../../types";
import { splitOverlapTokens } from "../../utils/textOverlap";

const props = defineProps<{ selected: HeatmapAnnotation }>();
const showInitialSource = ref(false);
watch(() => props.selected, () => { showInitialSource.value = false; });

const pct = (v: number) => (v > 1 ? v : v * 100).toFixed(1).replace(".", ",");
const isAiView = computed(() => props.selected.active_view === "AI" || props.selected.tier === "T3" || props.selected.color === "YELLOW");
const isResolved = computed(() => props.selected.color === "RESOLVED_GREEN" || (props.selected as any).match_type === "RESOLVED_GREEN");
const matchKindLabel = computed(() => (props.selected.tier === "T1" ? "Kata sama" : props.selected.tier === "T2" ? "Makna sama" : "Pola AI"));
const quoteTokens = computed(() => splitOverlapTokens(props.selected.matched_source_text || "", props.selected.text_snippet || ""));
const extraSources = computed(() => (props.selected.secondary_sources || []).slice(0, 3));
</script>

<template>
  <div class="mt-5 space-y-4 border-b border-[#E8ECEB] pb-5">
    <div>
      <p class="text-[13px] font-medium text-[#5E5A6B]">Kalimat di naskah Anda</p>
      <p class="mt-1 text-[15px] leading-relaxed text-[#14111C]">{{ selected.text_snippet || "Kalimat terpilih" }}</p>
    </div>

    <div v-if="isResolved" class="rounded-2xl border border-[#CBE6E1] bg-[#EBF8F6] p-3.5">
      <div class="flex items-center justify-between gap-2">
        <p class="text-[13px] font-semibold text-[#0F766E]">Sudah diperbaiki</p>
        <button v-if="selected.source_title || selected.matched_source_text" type="button" class="cursor-pointer text-[12.5px] font-medium text-[#0F766E] hover:underline" @click="showInitialSource = !showInitialSource">
          {{ showInitialSource ? "Sembunyikan sumber awal" : "Lihat sumber awal" }}
        </button>
      </div>
    </div>

    <div v-if="!isResolved || showInitialSource" class="space-y-3">
      <div class="flex items-baseline justify-between gap-4">
        <div class="min-w-0">
          <p class="text-[13px] font-medium text-[#5E5A6B]">
            {{ isAiView ? "Indikasi Pola Tulisan AI" : `${matchKindLabel} • ${selected.source_category || "Sumber Pembanding"}` }}
          </p>
          <p class="mt-0.5 text-[14px] font-semibold text-[#14111C]">{{ isAiView ? "Analisis Gaya Penulisan AI" : (selected.source_title || "Sumber pembanding") }}</p>
        </div>
        <p class="flex-shrink-0 text-[24px] font-semibold leading-none tracking-[-0.03em] tabular-nums text-[#14111C]">{{ pct(isAiView ? (selected.ai_score ?? selected.similarity ?? 0) : (selected.similarity ?? 0)) }}%</p>
      </div>

      <p v-if="isAiView" class="text-[13.5px] leading-relaxed text-[#4B4757]">{{ selected.ai_reason || selected.reason || "Struktur kalimat seragam atau terindikasi pola penulisan AI." }}</p>
      <div v-else class="rounded-2xl border border-[#E8ECEB] bg-[#F8FAFC] p-3.5">
        <p class="text-[12.5px] font-medium text-[#5E5A6B]">Kutipan pada sumber pembanding</p>
        <p v-if="selected.matched_source_text" class="mt-1.5 text-[13.5px] leading-relaxed text-[#14111C]">
          <template v-for="(tok, idx) in quoteTokens" :key="idx">
            <span v-if="tok.match" class="rounded bg-[#FEE2E2]/80 px-0.5 text-[#14111C]">{{ tok.text }}</span>
            <template v-else>{{ tok.text }}</template>
          </template>
        </p>
        <p v-else class="mt-1.5 text-[13px] italic text-[#5E5A6B]">Kutipan teks tidak tersedia dari sumber; kecocokan berbasis judul/snippet indeks.</p>
        <a v-if="selected.source_url" :href="selected.source_url" target="_blank" rel="noopener noreferrer" class="mt-2 inline-block text-[13px] font-medium text-[#0F766E] hover:underline">Buka sumber</a>
      </div>

      <div v-if="!isAiView && extraSources.length" class="space-y-1.5 border-t border-[#E8ECEB] pt-2.5">
        <p class="text-[12px] font-medium text-[#5E5A6B]">Sumber lain yang juga cocok</p>
        <div v-for="(sec, i) in extraSources" :key="i" class="flex items-baseline justify-between gap-2 text-[12.5px]">
          <span class="truncate text-[#4B4757]">{{ sec.source_title || "Sumber pembanding" }}</span>
          <span v-if="sec.similarity" class="flex-shrink-0 font-semibold tabular-nums text-[#5E5A6B]">{{ pct(sec.similarity) }}%</span>
        </div>
      </div>

      <p v-if="isAiView && selected.tier !== 'T3' && selected.source_title" class="text-[12.5px] text-[#5E5A6B]">Juga cocok dengan sumber: {{ selected.source_title }}</p>
      <p v-else-if="!isAiView && selected.ai_flag && selected.ai_reason" class="text-[12.5px] text-[#5E5A6B]">Juga terindikasi pola AI: {{ selected.ai_reason }}</p>
    </div>
  </div>
</template>
