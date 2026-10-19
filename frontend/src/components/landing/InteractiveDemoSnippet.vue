<script setup lang="ts">
import { ref } from "vue";

interface DemoSample {
  id: "T1" | "T2" | "T3";
  tierName: string;
  tierColor: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
  sourceType: string;
  originalText: string;
  matchedText: string;
  sourceDoc: string;
  similarityScore: number;
  metricLabel: string;
  metricValue: string;
  diagnostic: string;
}

const samples: DemoSample[] = [
  {
    id: "T1",
    tierName: "Tier 1: Leksikal",
    tierColor: "#EF4444",
    badgeBg: "bg-rose-50",
    badgeText: "text-rose-700",
    badgeBorder: "border-rose-200",
    sourceType: "Verbatim Plagiarism",
    originalText: "Algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    matchedText: "Algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    sourceDoc: "Skripsi Mahasiswa IF-2023 #DOC-0941",
    similarityScore: 100,
    metricLabel: "Rabin-Karp Hash Match",
    metricValue: "k=5, w=4 (Identik)",
    diagnostic: "100% kecocokan n-gram leksikal terdeteksi tanpa perubahan token atau urutan kata.",
  },
  {
    id: "T2",
    tierName: "Tier 2: Semantik",
    tierColor: "#F97316",
    badgeBg: "bg-orange-50",
    badgeText: "text-orange-800",
    badgeBorder: "border-orange-200",
    sourceType: "Intelligent Paraphrase",
    originalText: "Penerapan arsitektur jaringan saraf tiruan mampu meningkatkan efisiensi klasifikasi dokumen ilmiah secara signifikan.",
    matchedText: "Model deep learning terbukti mempercepat proses pengelompokan manuskrip riset akademik dengan tingkat akurasi tinggi.",
    sourceDoc: "Jurnal Rekayasa Sistem Vol. 8 #CORP-2201",
    similarityScore: 89.4,
    metricLabel: "HNSW Cosine Distance",
    metricValue: "d = 0.106 (Sim = 89.4%)",
    diagnostic: "Struktur leksikal diubah dengan sinonim, tetapi vektor representasi 384-dimensi menempati ruang semantik berjarak sangat dekat.",
  },
  {
    id: "T3",
    tierName: "Tier 3: Anomali Stilometri",
    tierColor: "#EAB308",
    badgeBg: "bg-amber-50",
    badgeText: "text-amber-800",
    badgeBorder: "border-amber-200",
    sourceType: "AI / LLM Generated Pattern",
    originalText: "Penting untuk dicatat bahwa dalam era digital ini, integritas akademik memainkan peranan yang sangat penting serta mendasar dalam menjaga kejujuran ilmiah.",
    matchedText: "Pola Sintaksis: Perulangan klise transisi ('Furthermore', 'Penting untuk dicatat') dengan varians panjang kalimat mendekati nol.",
    sourceDoc: "Dataset Benchmark Teks Sintesis LLM",
    similarityScore: 78.2,
    metricLabel: "Burstiness & TTR",
    metricValue: "Var(L) = 1.2, TTR = 0.38",
    diagnostic: "Panjang kalimat sangat seragam dan distribusi leksikal rendah, mengindikasikan teks digenerasi oleh model bahasa generatif.",
  },
];

const activeTab = ref<"T1" | "T2" | "T3">("T1");
const currentSample = ref<DemoSample>(samples[0]);

function selectSample(id: "T1" | "T2" | "T3") {
  activeTab.value = id;
  const found = samples.find((s) => s.id === id);
  if (found) currentSample.value = found;
}
</script>

<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4" aria-label="Demo Interaktif Deteksi">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-[#ededed] pb-5">
      <div>
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
          <span>Live Inspection Demo</span>
        </div>
        <h2 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight mt-2">
          Simulasi Cara Kerja <span class="italic font-normal text-[#17191c]">Engine Hybrid</span>
        </h2>
        <p class="text-xs text-[#777b86] mt-0.5 font-normal">
          Pilih salah satu tier untuk melihat bagaimana VeriText AI mendiagnosis kalimat naskah secara transparan.
        </p>
      </div>

      <!-- Steep Tab Group (Segmented pill control: rounded-full, mist background) -->
      <div class="inline-flex p-1 bg-[#f2f2f3] rounded-full border border-[#ededed] self-start sm:self-auto gap-1">
        <button
          v-for="s in samples"
          :key="s.id"
          type="button"
          :class="[
            'px-4 py-1.5 text-xs font-medium rounded-full transition-colors duration-150 ease-out select-none active:scale-[0.98]',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]',
            activeTab === s.id
              ? 'bg-[#17191c] text-white shadow-sm'
              : 'text-[#777b86] hover:text-[#17191c] hover:bg-white/60'
          ]"
          @click="selectSample(s.id)"
        >
          <span>{{ s.tierName }}</span>
        </button>
      </div>
    </div>

    <!-- Steep Diagnostic Viewer Card (24px radius, pure paper, hairline border) -->
    <div class="bg-white rounded-[24px] border border-[#ededed] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] space-y-4">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Input & Matched Text (Side-by-Side Diff) -->
        <div class="lg:col-span-8 space-y-3.5">
          <!-- Kalimat Dokumen Uji -->
          <div class="p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] space-y-2">
            <div class="flex items-center justify-between text-[11px]">
              <span class="uppercase font-medium text-[#777b86] tracking-wider">Kalimat Dokumen Uji</span>
              <span :class="['px-2.5 py-0.5 rounded-full text-[10px] font-medium border tabular-nums', currentSample.badgeBg, currentSample.badgeText, currentSample.badgeBorder]">
                {{ currentSample.sourceType }}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-[#17191c] leading-relaxed pl-2.5 border-l-2 font-normal" :style="{ borderColor: currentSample.tierColor }">
              "{{ currentSample.originalText }}"
            </p>
          </div>

          <!-- Sumber Rujukan Korpus -->
          <div class="p-4 rounded-[16px] border border-[#ededed] bg-white space-y-2">
            <div class="flex items-center justify-between text-[11px]">
              <span class="uppercase font-medium text-[#777b86] tracking-wider">Sumber Rujukan Korpus</span>
              <span class="text-[#979799] text-[10px] font-normal truncate max-w-[220px]">
                {{ currentSample.sourceDoc }}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-[#777b86] leading-relaxed pl-2.5 border-l-2 border-[#ededed] font-normal">
              "{{ currentSample.matchedText }}"
            </p>
          </div>
        </div>

        <!-- Metric Inspector Sidebar -->
        <div class="lg:col-span-4 p-5 rounded-[16px] border border-[#ededed] bg-[#fafafb] flex flex-col justify-between space-y-4">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-[#17191c]">Tingkat Kemiripan</span>
              <span class="text-2xl font-bold tabular-nums" :style="{ color: currentSample.tierColor }">
                {{ currentSample.similarityScore }}%
              </span>
            </div>

            <!-- Meter Bar (Crisp 1px border) -->
            <div class="w-full h-2 bg-[#ededed] rounded-full overflow-hidden border border-[#ededed]">
              <div
                class="h-full transition-all duration-200 ease-out rounded-full"
                :style="{ width: `${currentSample.similarityScore}%`, backgroundColor: currentSample.tierColor }"
              ></div>
            </div>

            <div class="pt-3 border-t border-[#ededed] space-y-1.5 text-[11px]">
              <div class="flex items-center justify-between">
                <span class="text-[#777b86] font-normal">Metrik Teknis</span>
                <span class="font-medium text-[#17191c] tabular-nums">{{ currentSample.metricValue }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[#777b86] font-normal">Algoritma</span>
                <span class="text-[#17191c] font-medium">{{ currentSample.metricLabel }}</span>
              </div>
            </div>
          </div>

          <div class="p-3.5 rounded-[12px] bg-white border border-[#ededed] text-[11px] text-[#777b86] leading-relaxed">
            <span class="font-medium text-[#17191c] block mb-0.5">Diagnosa Engine:</span>
            {{ currentSample.diagnostic }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
