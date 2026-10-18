<script setup lang="ts">
import SimilarityGauge from "../SimilarityGauge.vue";

interface Props {
  scoreComposite: number | null;
  scoreLexical: number | null;
  scoreSemantic: number | null;
  scoreStylometric: number | null;
}

withDefaults(defineProps<Props>(), {
  scoreComposite: 0,
  scoreLexical: 0,
  scoreSemantic: 0,
  scoreStylometric: 0,
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
    <div class="md:col-span-1 flex justify-center">
      <SimilarityGauge :score="scoreComposite ?? 0" />
    </div>

    <div class="md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Tier 1 Lexical Score -->
      <div class="bg-white border border-[#ededed] p-5 rounded-[14px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#fee2e2] transition-colors">
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-[#b91c1c] uppercase tracking-wider">
              Tier 1 &bull; Leksikal (50%)
            </span>
            <span class="w-2 h-2 rounded-full bg-[#EF4444]"></span>
          </div>
          <div class="text-3xl sm:text-4xl font-extrabold text-[#b91c1c] tabular-nums">
            {{ (scoreLexical ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#737373] mt-3 leading-relaxed font-normal">
          Algoritma Winnowing: Kecocokan string k-gram persis (<strong class="italic font-bold text-[#b91c1c]">verbatim match</strong>).
        </p>
      </div>

      <!-- Tier 2 Semantic Score -->
      <div class="bg-white border border-[#ededed] p-5 rounded-[14px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#ffedd5] transition-colors">
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-[#c2410c] uppercase tracking-wider">
              Tier 2 &bull; Semantik (35%)
            </span>
            <span class="w-2 h-2 rounded-full bg-[#F97316]"></span>
          </div>
          <div class="text-3xl sm:text-4xl font-extrabold text-[#c2410c] tabular-nums">
            {{ (scoreSemantic ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#737373] mt-3 leading-relaxed font-normal">
          pgvector HNSW: Kemiripan sudut kosinus vektor kalimat padat (&ge; 0.78).
        </p>
      </div>

      <!-- Tier 3 Stylometric Score -->
      <div class="bg-white border border-[#ededed] p-5 rounded-[14px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#fef08a] transition-colors">
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-[#854d0e] uppercase tracking-wider">
              Tier 3 &bull; Pola AI (15%)
            </span>
            <span class="w-2 h-2 rounded-full bg-[#EAB308]"></span>
          </div>
          <div class="text-3xl sm:text-4xl font-extrabold text-[#854d0e] tabular-nums">
            {{ (scoreStylometric ?? 0).toFixed(1) }}%
          </div>
        </div>
        <p class="text-[11px] text-[#737373] mt-3 leading-relaxed">
          Metrik Stilometri: Analisis Burstiness rendah & Type-Token Ratio sintetis model bahasa.
        </p>
      </div>
    </div>
  </div>
</template>
