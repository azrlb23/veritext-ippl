<script setup lang="ts">
import { ref } from "vue";

interface DemoSample {
  id: "T1" | "T2" | "T3";
  tierNumber: string;
  tierName: string;
  badgeLabel: string;
  colorHex: string;
  highlightBg: string;
  highlightBorder: string;
  originalText: string;
  highlightedSpan: string;
  postText: string;
  matchedSource: string;
  matchedAuthor: string;
  matchedSnippet: string;
  similarityScore: number;
  engineMetric: string;
  algorithmName: string;
  diagnosticNote: string;
}

const samples: DemoSample[] = [
  {
    id: "T1",
    tierNumber: "Tier 1",
    tierName: "Hashing Leksikal",
    badgeLabel: "Salin-Tempel Langsung",
    colorHex: "#EF4444",
    highlightBg: "bg-red-50 text-red-950",
    highlightBorder: "border-red-500",
    originalText: "Dalam pengujian ini terbukti bahwa ",
    highlightedSpan: "algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    postText: " Metode ini secara konsisten mempertahankan ketahanan terhadap transposisi kata.",
    matchedSource: "Skripsi Mahasiswa IF-2023 #DOC-0941",
    matchedAuthor: "Repositori Tugas Akhir Informatika",
    matchedSnippet: "algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    similarityScore: 100,
    engineMetric: "k=5, w=4 (Hash Identik)",
    algorithmName: "Rabin-Karp Rolling Hash",
    diagnosticNote: "100% kecocokan n-gram leksikal terdeteksi tanpa perubahan token atau urutan kata.",
  },
  {
    id: "T2",
    tierNumber: "Tier 2",
    tierName: "Semantik Dense",
    badgeLabel: "Parafrasa Cerdas",
    colorHex: "#F97316",
    highlightBg: "bg-orange-50 text-orange-950",
    highlightBorder: "border-orange-500",
    originalText: "Eksperimen membuktikan bahwa ",
    highlightedSpan: "penerapan arsitektur jaringan saraf tiruan mampu meningkatkan efisiensi klasifikasi dokumen ilmiah secara signifikan.",
    postText: " Hasil evaluasi menunjukkan konvergensi model yang lebih stabil.",
    matchedSource: "Jurnal Rekayasa Sistem Vol. 8 #CORP-2201",
    matchedAuthor: "Arsip Jurnal Nasional Terakreditasi",
    matchedSnippet: "model deep learning terbukti mempercepat proses pengelompokan manuskrip riset akademik dengan tingkat akurasi tinggi.",
    similarityScore: 89.4,
    engineMetric: "Jarak Kosinus d = 0.106",
    algorithmName: "pgvector HNSW (384 Dimensi)",
    diagnosticNote: "Struktur kalimat dan kosakata diubah dengan sinonim, tetapi vektor representasi 384D menempati ruang semantik berjarak sangat dekat.",
  },
  {
    id: "T3",
    tierNumber: "Tier 3",
    tierName: "Stilometri AI",
    badgeLabel: "Sintaksis Model LLM",
    colorHex: "#EAB308",
    highlightBg: "bg-amber-50 text-amber-950",
    highlightBorder: "border-amber-500",
    originalText: "Sebagai landasan berpikir, ",
    highlightedSpan: "penting untuk dicatat bahwa dalam era digital ini, integritas akademik memainkan peranan yang sangat penting serta mendasar dalam menjaga kejujuran ilmiah.",
    postText: " Hal ini menjadi pilar utama pembentukan karakter civitas akademika.",
    matchedSource: "Dataset Sintesis LLM Benchmark 2026",
    matchedAuthor: "Pola Sintaksis Generator AI",
    matchedSnippet: "Pola anomali: Kalimat transisi klise berulang dengan varians deviasi panjang kalimat mendekati nol (monoton).",
    similarityScore: 78.2,
    engineMetric: "Burstiness = 0.12, TTR = 0.38",
    algorithmName: "Varians Panjang & Type-Token Ratio",
    diagnosticNote: "Panjang kalimat sangat seragam dan distribusi leksikal rendah, mengindikasikan teks digenerasi otomatis oleh model bahasa AI.",
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
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 select-none" aria-label="Simulasi Diagnostik Naskah">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#ededed] pb-6 mb-8">
      <div class="space-y-2">
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
          <span>Inspeksi Dokumen Real-Time</span>
        </div>
        <h2 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
          Cara Kerja Engine <span class="italic font-normal text-[#17191c]">Mendiagnosis Naskah</span>
        </h2>
        <p class="text-sm text-[#777b86] font-normal max-w-xl">
          Pilih salah satu tingkat pengujian untuk melihat bagaimana sistem menandai kalimat secara transparan bersama bukti pembandingnya.
        </p>
      </div>

      <!-- Segmented Pill Tabs (Steep Quiet Controls) -->
      <div class="inline-flex p-1 bg-[#f2f2f3] rounded-full border border-[#ededed] self-start md:self-auto gap-1">
        <button
          v-for="s in samples"
          :key="s.id"
          type="button"
          :class="[
            'px-4 py-2 text-xs font-medium rounded-full transition-all duration-150 ease-out select-none',
            'focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c]',
            activeTab === s.id
              ? 'bg-[#17191c] text-white shadow-sm'
              : 'text-[#777b86] hover:text-[#17191c] hover:bg-white/50'
          ]"
          @click="selectSample(s.id)"
        >
          <span class="font-semibold">{{ s.tierNumber }}:</span> {{ s.tierName }}
        </button>
      </div>
    </div>

    <!-- Editorial Manuscript Inspection Canvas -->
    <div class="bg-white rounded-[28px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_40px_-15px_rgba(0,0,0,0.08)] overflow-hidden">
      <!-- Canvas Top Metadata Bar -->
      <div class="h-11 bg-[#fafafb] border-b border-[#ededed] px-6 flex items-center justify-between text-xs text-[#777b86]">
        <div class="flex items-center space-x-3">
          <span class="font-medium text-[#17191c]">Naskah Uji vs Repositori Korpus</span>
          <span class="text-[#ededed]">&bull;</span>
          <span class="inline-flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: currentSample.colorHex }"></span>
            <span class="font-medium text-[#17191c]">{{ currentSample.badgeLabel }}</span>
          </span>
        </div>
        <div class="hidden sm:flex items-center space-x-2 font-mono text-[11px]">
          <span>Algoritma: <strong class="text-[#17191c]">{{ currentSample.algorithmName }}</strong></span>
        </div>
      </div>

      <!-- Main Split View: Left Document Passage, Right Side-by-Side Match -->
      <div class="grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-[#ededed]">
        <!-- Left Column: Authentic Manuscript Excerpt (7 Cols) -->
        <div class="lg:col-span-7 p-6 sm:p-8 space-y-5 bg-white">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold text-[#979799] uppercase tracking-wider font-mono">
              Fragmen Naskah Dokumen Mahasiswa
            </span>
            <span class="text-[11px] text-[#777b86]">Bab II &bull; Tinjauan Pustaka</span>
          </div>

          <!-- Document Paragraph with Editorial Highlight -->
          <div class="p-6 rounded-[20px] bg-[#fafafb] border border-[#ededed] leading-relaxed text-sm sm:text-base text-[#17191c]">
            <span class="text-[#777b86]">{{ currentSample.originalText }}</span>
            <mark
              :class="[
                'px-1.5 py-0.5 rounded-md font-medium border-b-2 transition-colors duration-150',
                currentSample.highlightBg,
                currentSample.highlightBorder
              ]"
            >
              "{{ currentSample.highlightedSpan }}"
            </mark>
            <span class="text-[#777b86]">{{ currentSample.postText }}</span>
          </div>

          <!-- Diagnostic Note Callout -->
          <div class="p-4 rounded-[16px] border border-[#ededed] bg-white flex items-start space-x-3">
            <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-white text-xs font-bold" :style="{ backgroundColor: currentSample.colorHex }">
              !
            </div>
            <div class="space-y-0.5 text-xs">
              <div class="font-semibold text-[#17191c]">Catatan Hasil Diagnosis:</div>
              <p class="text-[#777b86] leading-relaxed font-normal">
                {{ currentSample.diagnosticNote }}
              </p>
            </div>
          </div>
        </div>

        <!-- Right Column: Matched Reference Source & Technical Metrics (5 Cols) -->
        <div class="lg:col-span-5 p-6 sm:p-8 space-y-6 bg-[#fafafb] flex flex-col justify-between">
          <div class="space-y-5">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-bold text-[#979799] uppercase tracking-wider font-mono">
                Rujukan Pembanding Korpus
              </span>
              <span class="text-xs font-bold tabular-nums px-2.5 py-0.5 rounded-full bg-white border border-[#ededed]" :style="{ color: currentSample.colorHex }">
                {{ currentSample.similarityScore }}% Kecocokan
              </span>
            </div>

            <!-- Matched Snippet Box -->
            <div class="p-5 rounded-[20px] bg-white border border-[#ededed] space-y-2 shadow-sm">
              <div class="text-[11px] font-semibold text-[#17191c] truncate">
                {{ currentSample.matchedSource }}
              </div>
              <div class="text-[10px] text-[#777b86] -mt-1">
                {{ currentSample.matchedAuthor }}
              </div>
              <p class="text-xs text-[#515151] italic leading-relaxed pt-2 border-t border-[#ededed]">
                "{{ currentSample.matchedSnippet }}"
              </p>
            </div>

            <!-- Technical Parameter Checklist -->
            <div class="space-y-2 text-xs">
              <div class="flex items-center justify-between py-1.5 border-b border-[#ededed]">
                <span class="text-[#777b86]">Metrik Nilai</span>
                <span class="font-mono font-medium text-[#17191c] tabular-nums">{{ currentSample.engineMetric }}</span>
              </div>
              <div class="flex items-center justify-between py-1.5 border-b border-[#ededed]">
                <span class="text-[#777b86]">Algoritma Inti</span>
                <span class="font-medium text-[#17191c]">{{ currentSample.algorithmName }}</span>
              </div>
              <div class="flex items-center justify-between py-1.5">
                <span class="text-[#777b86]">Bobot Komposit</span>
                <span class="font-semibold text-[#17191c] tabular-nums">
                  {{ currentSample.id === 'T1' ? '50%' : currentSample.id === 'T2' ? '35%' : '15%' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Bottom Action Link -->
          <div class="pt-4 border-t border-[#ededed]">
            <router-link
              to="/dashboard"
              class="w-full inline-flex items-center justify-center px-4 py-2.5 rounded-full bg-[#17191c] hover:bg-[#2b2e34] text-white text-xs font-medium transition-colors"
            >
              <span>Coba Uji Naskah Lengkap di Workspace</span>
              <span class="ml-1.5">&rarr;</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
