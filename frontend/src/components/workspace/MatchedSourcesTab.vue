<script setup lang="ts">
import type { HeatmapAnnotation, MatchedSource } from "../../types";

defineProps<{
  selectedSentence?: HeatmapAnnotation | null;
  matchedSources: MatchedSource[];
}>();

const emit = defineEmits<{
  (e: "request-paraphrase", sentence: HeatmapAnnotation): void;
}>();
</script>

<template>
  <div class="space-y-5">
    <div class="bg-white border border-[#E4E8F0] rounded-2xl p-5 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold uppercase tracking-wider text-gray-700">
          Perbandingan Kalimat Terpilih
        </h3>
        <span
          v-if="selectedSentence"
          class="px-2.5 py-0.5 text-xs font-semibold rounded-full tabular-nums"
          :class="selectedSentence.color === 'RESOLVED_GREEN' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'"
        >
          Kemiripan: {{ ((selectedSentence.similarity ?? 0.8) * 100).toFixed(1) }}%
        </span>
      </div>

      <div v-if="selectedSentence" class="space-y-3">
        <div class="p-3 bg-gray-50 border border-gray-200 rounded-xl space-y-1">
          <span class="text-[11px] font-semibold text-gray-500 uppercase tracking-tight">Kalimat Naskah</span>
          <p class="text-xs text-gray-800 leading-relaxed font-serif">
            "{{ selectedSentence.text_snippet || 'Teks kalimat naskah...' }}"
          </p>
        </div>

        <div class="p-3 bg-amber-50/50 border border-amber-200 rounded-xl space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-amber-800 uppercase tracking-tight">Kutipan Sumber Pembanding</span>
            <span class="text-[10px] text-amber-700 font-medium truncate max-w-[200px]">
              {{ selectedSentence.source_title || 'Pangkalan Korpus' }}
            </span>
          </div>
          <p class="text-xs text-amber-950 leading-relaxed italic">
            "{{ selectedSentence.reason || selectedSentence.text_snippet || 'Kutipan teks pembanding dari korpus rujukan.' }}"
          </p>
        </div>

        <button
          type="button"
          @click="emit('request-paraphrase', selectedSentence)"
          class="w-full py-2.5 px-4 bg-[#1560BD] hover:bg-[#1A73D9] text-white text-xs font-semibold rounded-xl shadow-sm transition-all flex items-center justify-center space-x-1.5"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>Parafrase Kalimat Ini dengan AI</span>
        </button>
      </div>

      <div v-else class="text-xs text-gray-400 py-6 text-center italic">
        Klik salah satu kalimat tersorot pada naskah untuk melihat diff perbandingan dan opsi parafrase AI.
      </div>
    </div>

    <div class="bg-white border border-[#E4E8F0] rounded-2xl p-5 shadow-sm space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold uppercase tracking-wider text-gray-700">
          Daftar Sumber Kemiripan
        </h3>
        <span class="text-xs text-gray-500 font-medium">{{ matchedSources.length }} Sumber Terdeteksi</span>
      </div>

      <div v-if="matchedSources.length > 0" class="divide-y divide-gray-100 max-h-[320px] overflow-y-auto pr-1">
        <div v-for="(src, idx) in matchedSources" :key="idx" class="py-3 first:pt-0 last:pb-0 space-y-1">
          <div class="flex items-start justify-between gap-2">
            <span class="text-xs font-semibold text-gray-800 line-clamp-2">{{ src.title }}</span>
            <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200 tabular-nums flex-shrink-0">
              {{ (src.contribution_pct * 100 > 100 ? src.contribution_pct : src.contribution_pct * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="flex items-center justify-between text-[11px] text-gray-500">
            <span>{{ src.category || 'Arsip Dokumen' }}</span>
            <a
              v-if="src.source_url"
              :href="src.source_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-[#1560BD] hover:underline font-medium"
            >
              Buka Dokumen
            </a>
            <span v-else class="text-gray-400 italic">Korpus Terdaftar</span>
          </div>
        </div>
      </div>

      <div v-else class="text-xs text-gray-400 py-4 text-center italic">
        Tidak ada sumber eksternal yang cocok.
      </div>
    </div>
  </div>
</template>
