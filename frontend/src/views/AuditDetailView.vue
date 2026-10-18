<script setup lang="ts">
import { ref, onMounted } from "vue";
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
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Loading State -->
    <div v-if="isLoading" class="p-12 text-center bg-white rounded-[14px] border border-[#ededed] shadow-audyr-subtle">
      <div class="w-8 h-8 border-2 border-audyr-ink border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-sm font-medium text-audyr-ink">Memuat data laporan audit dari server...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage || !reportData" class="p-8 text-center bg-white rounded-[14px] border border-rose-200 shadow-audyr-subtle space-y-4">
      <div class="inline-flex p-3 rounded-full bg-rose-50 text-rose-600 mb-2">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="text-lg font-bold text-audyr-ink">Laporan Audit Tidak Tersedia</h2>
      <p class="text-xs text-audyr-ash max-w-md mx-auto">{{ errorMessage }}</p>
      <router-link
        to="/dashboard"
        class="inline-block px-4 py-2 text-xs font-semibold text-white bg-audyr-ink rounded-[4px] hover:bg-black transition-colors"
      >
        Kembali ke Workspace Dashboard
      </router-link>
    </div>

    <!-- Data Loaded State -->
    <template v-else>
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-[14px] border border-[#ededed] shadow-audyr-subtle">
        <div class="space-y-1.5">
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] italic font-bold tracking-tight bg-audyr-mint-whisper text-[#065f46] border border-[#a7f3d0]">
              Audit Selesai
            </span>
            <span class="text-xs tabular-nums text-audyr-ash">ID: <span class="font-bold text-audyr-ink">{{ reportData.id }}</span> &bull; UUID: <span class="font-bold text-audyr-ink">{{ reportData.verification_uuid }}</span></span>
          </div>
          <h1 class="text-xl sm:text-2xl font-extrabold text-audyr-ink tracking-tight">
            {{ reportData.document_title }}
          </h1>
          <p class="text-xs text-audyr-ash">
            Diperiksa oleh: <span class="font-bold text-audyr-ink">{{ reportData.user_name }}</span> ({{ reportData.institution }}) &bull; Waktu: <span class="tabular-nums font-medium">{{ reportData.generated_at }}</span>
          </p>
        </div>

        <!-- Action Buttons -->
        <ExportReportActions
          :verificationUuid="reportData.verification_uuid"
          @exportPdf="handleExportPdf"
        />
      </div>

      <!-- Scores Overview Card (Composite + 3 Tiers) -->
      <ScoreSummaryCard
        :scoreComposite="reportData.score_composite"
        :scoreLexical="reportData.score_lexical"
        :scoreSemantic="reportData.score_semantic"
        :scoreStylometric="reportData.score_stylometric"
      />

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
