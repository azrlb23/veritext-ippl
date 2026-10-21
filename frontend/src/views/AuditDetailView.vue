<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  ScoreSummaryCard,
  SideBySideDiff,
  SentenceDetailModal,
  ExportReportActions,
  MatchedSourcesTable,
  HeatmapViewer,
  TierLegend,
  type HeatmapAnnotation,
  type MatchedSource,
} from "../components/audit";
import { useModal, useNotification } from "../composables";
import { auditService } from "../services/auditService";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const reportId = (route.params.id as string) || "";
const { showNotification } = useNotification();
const { isOpen: isDetailModalOpen, open: openDetailModal, close: closeDetailModal } = useModal();
const authStore = useAuthStore();

const isLoading = ref(true);
const errorMessage = ref("");
const selectedAnnotation = ref<HeatmapAnnotation | null>(null);

const reportData = ref<{
  id: string;
  document_title: string;
  verification_uuid: string;
  generated_at: string;
  user_name: string;
  institution: string;
  score_lexical: number;
  score_semantic: number;
  score_stylometric: number;
  score_composite: number;
} | null>(null);

const annotations = ref<HeatmapAnnotation[]>([]);
const matchedSources = ref<MatchedSource[]>([]);

onMounted(async () => {
  if (!reportId) {
    errorMessage.value = "ID Laporan audit tidak ditentukan.";
    isLoading.value = false;
    return;
  }
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await auditService.getReport(reportId);
    if (data) {
      reportData.value = {
        id: data.id || reportId,
        document_title: data.document_title || "Naskah Akademik",
        verification_uuid: data.verification_uuid || "-",
        generated_at: data.generated_at
          ? new Date(data.generated_at).toLocaleString("id-ID", {
              dateStyle: "long",
              timeStyle: "short",
            })
          : "Waktu tidak tersedia",
        user_name: data.user_name || authStore.user?.full_name || "Pengguna VeriText",
        institution: data.institution || authStore.user?.institution || "Institusi",
        score_lexical: data.score_lexical ?? 0,
        score_semantic: data.score_semantic ?? 0,
        score_stylometric: data.score_stylometric ?? 0,
        score_composite: data.score_composite ?? 0,
      };
      annotations.value = data.heatmap_annotations || [];
      matchedSources.value = data.matched_sources || [];
    } else {
      errorMessage.value = "Laporan audit tidak ditemukan di sistem.";
    }
  } catch (err: any) {
    errorMessage.value =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      "Gagal memuat laporan audit dari server.";
  } finally {
    isLoading.value = false;
  }
});

function handleAnnotationSelected(anno: HeatmapAnnotation) {
  selectedAnnotation.value = anno;
  openDetailModal();
}

async function handleExportPdf() {
  if (!reportData.value) return;
  showNotification(
    "Menyiapkan sertifikat resmi ber-QR Code...",
    "info",
    "Memproses PDF"
  );
  try {
    const filename = await auditService.downloadPdfReport(
      reportData.value.id,
      reportData.value.document_title || "Naskah"
    );
    showNotification(
      `Sertifikat berhasil diunduh sebagai ${filename}`,
      "success",
      "Unduh Berhasil"
    );
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal mengunduh berkas sertifikat PDF.",
      "error",
      "Unduh Gagal"
    );
  }
}

// Key Findings Narrative Synthesizer (Editorial Magazine Style)
const keyFindings = computed(() => {
  if (!reportData.value) return null;
  const { score_lexical, score_semantic, score_stylometric, score_composite } = reportData.value;

  const lexicalText = score_lexical <= 15
    ? "Kecocokan leksikal verbatim sangat rendah (" + score_lexical.toFixed(1) + "%). Algoritma Rabin-Karp tidak mendeteksi segmen salin-tempel langsung yang melebihi batas toleransi sitasi wajar."
    : "Ditemukan beberapa blok teks (" + score_lexical.toFixed(1) + "%) dengan kecocokan n-gram verbatim persis terhadap repositori rujukan yang memerlukan sitasi atau tanda kutip langsung.";

  const semanticText = score_semantic <= 20
    ? "Kedekatan semantik dense 384-dimensi berada dalam zona orisinal (" + score_semantic.toFixed(1) + "%). Pola kalimat memiliki representasi konseptual khas yang tidak mencerminkan parafrasa dangkal."
    : "Terindikasi parafrasa berdensitas cukup tinggi (" + score_semantic.toFixed(1) + "%). Jarak kosinus pgvector HNSW mendeteksi kemiripan struktur gagasan dengan korpus yang tersimpan.";

  const stylometricText = score_stylometric <= 15
    ? "Pola stilometri (" + score_stylometric.toFixed(1) + "%) memperlihatkan variasi burstiness dan Type-Token Ratio alami khas tulisan manusia otentik."
    : "Ditemukan homogenitas panjang klausa dan leksikon sintaksis (" + score_stylometric.toFixed(1) + "%) yang konsisten dengan karakteristik generasi model bahasa AI.";

  const recommendation = score_composite <= 20
    ? "Naskah memenuhi standar integritas karya ilmiah perguruan tinggi. Layak diajukan untuk proses review sejawat atau sidang akademik."
    : "Naskah disarankan untuk dilakukan parafrasa ulang pada bagian tertandai merah/oranye serta melengkapi rujukan sumber primer.";

  return {
    lexicalText,
    semanticText,
    stylometricText,
    recommendation,
    statusLevel: score_composite <= 20 ? "MEMENUHI SYARAT" : "PERLU TINJAUAN",
  };
});
</script>

<template>
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Ambient Warm Peach Radial Glow -->
    <div
      class="absolute top-0 left-1/2 -translate-x-1/2 -z-10 w-full max-w-6xl h-[450px] bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(251,225,209,0.55),rgba(255,255,255,0))] blur-3xl pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Loading State -->
    <div v-if="isLoading" class="p-16 text-center bg-white rounded-[24px] border border-[#ededed] shadow-sm">
      <div class="w-8 h-8 border-2 border-[#17191c] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-medium text-[#17191c]">Memuat data laporan audit dari server...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage || !reportData" class="p-8 text-center bg-white rounded-[24px] border border-rose-200 shadow-sm space-y-4">
      <div class="inline-flex p-3 rounded-full bg-rose-50 text-rose-600 mb-2">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="text-lg font-bold text-[#17191c]">Laporan Audit Tidak Tersedia</h2>
      <p class="text-xs text-[#777b86] max-w-md mx-auto">{{ errorMessage }}</p>
      <router-link
        to="/dashboard"
        class="inline-block px-5 py-2.5 text-xs font-medium text-white bg-[#17191c] rounded-full hover:bg-[#2e3138] transition-colors"
      >
        Kembali ke Workspace Dashboard
      </router-link>
    </div>

    <!-- Data Loaded State -->
    <template v-else>
      <!-- Header Window Shell -->
      <div class="bg-white p-6 sm:p-8 rounded-[24px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="space-y-2">
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-3 py-0.5 rounded-full text-[11px] font-semibold tracking-tight bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
              Audit Terverifikasi
            </span>
            <span class="text-xs tabular-nums text-[#777b86] font-mono">
              ID: <span class="font-medium text-[#17191c]">{{ reportData.id.slice(0, 8) }}...</span> &bull; UUID: <span class="font-medium text-[#17191c]">{{ reportData.verification_uuid }}</span>
            </span>
          </div>

          <!-- Document Title with Serif Typography -->
          <h1 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight">
            {{ reportData.document_title }}
          </h1>

          <p class="text-xs text-[#777b86] font-normal">
            Diperiksa oleh: <strong class="font-medium text-[#17191c]">{{ reportData.user_name }}</strong> ({{ reportData.institution }}) &bull; Waktu: <span class="tabular-nums font-normal">{{ reportData.generated_at }}</span>
          </p>
        </div>

        <!-- Action Buttons (Pill-shaped) -->
        <ExportReportActions
          :verificationUuid="reportData.verification_uuid"
          @exportPdf="handleExportPdf"
        />
      </div>

      <!-- Scores Overview Card (Composite Donut Gauge + 3 Tiers) -->
      <ScoreSummaryCard
        :scoreComposite="reportData.score_composite"
        :scoreLexical="reportData.score_lexical"
        :scoreSemantic="reportData.score_semantic"
        :scoreStylometric="reportData.score_stylometric"
      />

      <!-- ============================================================ -->
      <!-- EDITORIAL NARRATIVE: Key Findings & Diagnostic Notes         -->
      <!-- ============================================================ -->
      <div
        v-if="keyFindings"
        class="bg-white rounded-[24px] p-6 sm:p-8 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] space-y-5"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#ededed] pb-4">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="text-[10px] uppercase font-bold tracking-wider text-[#5d2a1a] bg-[#fbe1d1] px-2.5 py-0.5 rounded-full">
                AI Editorial Synthesis
              </span>
              <span class="text-xs text-[#777b86] font-mono">Key Findings &amp; Diagnostics</span>
            </div>
            <h2 class="font-serif text-xl sm:text-2xl font-normal text-[#17191c] tracking-tight">
              Catatan Diagnostik &amp; Temuan Kunci Integritas Naskah
            </h2>
          </div>
          <span
            class="self-start sm:self-auto text-xs px-3.5 py-1 rounded-full font-semibold uppercase tracking-wider"
            :class="keyFindings.statusLevel === 'MEMENUHI SYARAT' ? 'bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]' : 'bg-[#fff7ed] text-[#c2410c] border border-[#ffedd5]'"
          >
            {{ keyFindings.statusLevel }}
          </span>
        </div>

        <!-- 3-Column Narrative Editorial Findings -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs">
          <!-- Finding 1: Tier 1 -->
          <div class="space-y-2 p-4 rounded-[18px] bg-[#fafafb] border border-[#ededed]">
            <div class="flex items-center justify-between">
              <span class="font-bold text-[#b91c1c] uppercase tracking-wider text-[10px]">Tier 1 &bull; Leksikal Verbatim</span>
              <span class="text-[10px] font-mono font-bold text-[#b91c1c]">{{ reportData.score_lexical.toFixed(1) }}%</span>
            </div>
            <p class="text-[#777b86] leading-relaxed font-normal">
              {{ keyFindings.lexicalText }}
            </p>
          </div>

          <!-- Finding 2: Tier 2 -->
          <div class="space-y-2 p-4 rounded-[18px] bg-[#fafafb] border border-[#ededed]">
            <div class="flex items-center justify-between">
              <span class="font-bold text-[#c2410c] uppercase tracking-wider text-[10px]">Tier 2 &bull; Parafrasa Semantik</span>
              <span class="text-[10px] font-mono font-bold text-[#c2410c]">{{ reportData.score_semantic.toFixed(1) }}%</span>
            </div>
            <p class="text-[#777b86] leading-relaxed font-normal">
              {{ keyFindings.semanticText }}
            </p>
          </div>

          <!-- Finding 3: Tier 3 -->
          <div class="space-y-2 p-4 rounded-[18px] bg-[#fafafb] border border-[#ededed]">
            <div class="flex items-center justify-between">
              <span class="font-bold text-[#854d0e] uppercase tracking-wider text-[10px]">Tier 3 &bull; Pola AI &amp; Stilometri</span>
              <span class="text-[10px] font-mono font-bold text-[#854d0e]">{{ reportData.score_stylometric.toFixed(1) }}%</span>
            </div>
            <p class="text-[#777b86] leading-relaxed font-normal">
              {{ keyFindings.stylometricText }}
            </p>
          </div>
        </div>

        <!-- Editorial Verdict Banner -->
        <div class="p-4 rounded-[18px] bg-[#f2f2f3] border border-[#ededed] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div class="flex items-start sm:items-center space-x-2.5">
            <span class="w-2 h-2 rounded-full bg-[#17191c] mt-1 sm:mt-0 flex-shrink-0"></span>
            <span class="text-[#17191c] leading-relaxed">
              <strong class="font-semibold">Rekomendasi Panel Audit:</strong> {{ keyFindings.recommendation }}
            </span>
          </div>
          <span class="text-[10px] text-[#777b86] font-mono flex-shrink-0 self-end sm:self-auto">
            UU PDP No. 27/2022 Verified
          </span>
        </div>
      </div>

      <!-- Tier Legend -->
      <TierLegend showControls />

      <!-- Interactive Heatmap Viewer -->
      <HeatmapViewer
        :annotations="annotations"
        @selectAnnotation="handleAnnotationSelected"
      />

      <!-- Side-by-Side Comparison -->
      <SideBySideDiff
        :annotations="annotations"
        @selectAnnotation="handleAnnotationSelected"
      />

      <!-- Matched Corpus Sources Breakdown -->
      <MatchedSourcesTable :sources="matchedSources" />

      <!-- Sentence Detail Modal -->
      <SentenceDetailModal
        :isOpen="isDetailModalOpen"
        :annotation="selectedAnnotation"
        @close="closeDetailModal"
      />
    </template>
  </div>
</template>
