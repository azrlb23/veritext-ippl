<script setup lang="ts">
import { ref } from "vue";
import type { HeatmapAnnotation } from "../types";

defineProps<{
  text?: string;
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
  if (tier === "T1" && showT1.value) return "highlight-t1 cursor-pointer font-medium";
  if (tier === "T2" && showT2.value) return "highlight-t2 cursor-pointer font-medium";
  if (tier === "T3" && showT3.value) return "highlight-t3 cursor-pointer font-medium";
  return "";
}

function selectAnno(anno: HeatmapAnnotation) {
  selectedAnnotation.value = anno;
  emit("selectAnnotation", anno);
}
</script>

<template>
  <div class="space-y-4">
    <!-- Tier Filtering Toggles -->
    <div class="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle">
      <div class="flex items-center space-x-2 text-xs font-semibold text-audyr-ink tracking-tight">
        <span>Filter Lapisan Sorotan:</span>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          @click="showT1 = !showT1"
          class="px-2.5 py-1 text-xs font-medium rounded-[4px] border transition-all flex items-center"
          :class="showT1 ? 'bg-red-50 text-red-700 border-red-300 ring-1 ring-red-300' : 'bg-white text-audyr-ash border-[#ededed] hover:border-audyr-ink'"
        >
          <span>Tier 1 Leksikal (Merah)</span>
        </button>

        <button
          type="button"
          @click="showT2 = !showT2"
          class="px-2.5 py-1 text-xs font-medium rounded-[4px] border transition-all flex items-center"
          :class="showT2 ? 'bg-orange-50 text-orange-700 border-orange-300 ring-1 ring-orange-300' : 'bg-white text-audyr-ash border-[#ededed] hover:border-audyr-ink'"
        >
          <span>Tier 2 Semantik (Oranye)</span>
        </button>

        <button
          type="button"
          @click="showT3 = !showT3"
          class="px-2.5 py-1 text-xs font-medium rounded-[4px] border transition-all flex items-center"
          :class="showT3 ? 'bg-yellow-50 text-yellow-800 border-yellow-300 ring-1 ring-yellow-300' : 'bg-white text-audyr-ash border-[#ededed] hover:border-audyr-ink'"
        >
          <span>Tier 3 AI (Kuning)</span>
        </button>
      </div>
    </div>

    <!-- Heatmap Document Text Viewer -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2 bg-white border border-[#ededed] rounded-[14px] p-6 shadow-audyr-subtle leading-relaxed text-sm text-audyr-ink space-y-4">
        <h3 class="text-sm font-extrabold text-[#262626] uppercase tracking-wide mb-2">
          Naskah Dokumen dengan <span class="italic font-bold text-[#686868]">Interactive Heatmap</span>
        </h3>

        <!-- Text snippets rendered with highlights -->
        <div class="prose max-w-none text-audyr-slate space-y-3 font-normal leading-[1.75]">
          <p>
            Perkembangan teknologi kecerdasan buatan telah mengubah lanskap publikasi ilmiah secara dramatis.
            <span
              @click="annotations[0] && selectAnno(annotations[0])"
              :class="getHighlightClass('T1')"
              title="Klik untuk melihat sumber leksikal"
            >
              Implementasi sistem deteksi plagiarisme cerdas memerlukan integrasi antara pemrosesan bahasa alami deterministik dan representasi vektor bernuansa semantik.
            </span>
            Hal ini penting untuk memastikan orisinalitas riset tetap terjaga tanpa menghambat inovasi.
          </p>

          <p>
            Dalam pengujian awal terhadap dokumen akademik berskala besar,
            <span
              @click="annotations[1] && selectAnno(annotations[1])"
              :class="getHighlightClass('T2')"
              title="Klik untuk melihat kemiripan semantik"
            >
              pendekatan berbasis representasi vektor padat kalimat membuktikan efektivitas tinggi dalam mengenali parafrasa terstruktur yang lolos dari algoritma leksikal konvensional.
            </span>
            Metode ini mampu memetakan kedekatan sudut kosinus antar pasangan kalimat dalam ruang laten multi-dimensi.
          </p>

          <p>
            <span
              @click="annotations[2] && selectAnno(annotations[2])"
              :class="getHighlightClass('T3')"
              title="Klik untuk melihat anomali AI"
            >
              Karakteristik teks memiliki keragaman leksikal yang seragam serta variasi panjang kalimat yang konsisten rendah, mengindikasikan karakteristik khas sintesis otomatis oleh model bahasa generatif.
            </span>
            Oleh karena itu, penggabungan metrik stilometri menjadi krusial untuk melengkapi evaluasi integritas akademik secara menyeluruh.
          </p>
        </div>
      </div>

      <!-- Detail Card on Selected Highlight -->
      <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-4">
        <h4 class="text-xs font-extrabold uppercase tracking-wide text-audyr-ash">
          Detail Temuan Terpilih
        </h4>

        <div v-if="selectedAnnotation" class="space-y-3">
          <div class="flex items-center justify-between">
            <span
              class="px-2.5 py-0.5 text-xs font-bold rounded-full"
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
            <span class="text-sm font-extrabold text-audyr-ink tabular-nums">
              Sim: {{ (selectedAnnotation.similarity * 100).toFixed(1) }}%
            </span>
          </div>

          <div>
            <div class="text-[11px] font-semibold text-audyr-ash uppercase tracking-tight">Sumber Pembanding</div>
            <div class="text-xs font-medium text-audyr-ink mt-0.5">
              {{ selectedAnnotation.source_title || "Pola Korpus Terdaftar" }}
            </div>
          </div>

          <div>
            <div class="text-[11px] font-semibold text-audyr-ash uppercase tracking-tight">Kutipan Teks Sumber</div>
            <div class="text-xs italic bg-white border border-[#ededed] p-2.5 rounded-[8px] text-audyr-slate mt-0.5 shadow-audyr-subtle">
              "{{ selectedAnnotation.text_snippet }}"
            </div>
          </div>
        </div>

        <div v-else class="text-center py-10 text-xs text-audyr-ash">
          Klik salah satu kalimat berwarna pada naskah untuk melihat perbandingan sumber dan skor kemiripan rincian.
        </div>
      </div>
    </div>
  </div>
</template>
