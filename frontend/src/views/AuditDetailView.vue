<script setup lang="ts">
import { ref } from "vue";
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

const route = useRoute();
const reportId = (route.params.id as string) || "task-001";
const { showNotification } = useNotification();
const { isOpen: isDetailModalOpen, open: openDetailModal, close: closeDetailModal } = useModal();

const selectedAnnotation = ref<HeatmapAnnotation | null>(null);

// Report data based on SDD specs
const reportData = ref({
  id: reportId,
  document_title: "Pengaruh Algoritma Rekomendasi Terhadap Polaritas Opini Publik.pdf",
  verification_uuid: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  generated_at: "11 Oktober 2026, 20:30 WIB",
  user_name: "Dr. Budi Santoso",
  institution: "Universitas Indonesia",
  score_lexical: 14.5,
  score_semantic: 18.2,
  score_stylometric: 8.0,
  score_composite: 14.8,
});

const annotations = ref<HeatmapAnnotation[]>([
  {
    start: 0,
    end: 120,
    tier: "T1",
    color: "RED",
    source_title: "Jurnal Informatika Vol. 12 (2023)",
    similarity: 0.98,
    text_snippet: "Implementasi sistem deteksi plagiarisme cerdas memerlukan integrasi antara pemrosesan bahasa alami deterministik...",
  },
  {
    start: 140,
    end: 285,
    tier: "T2",
    color: "ORANGE",
    source_title: "Prosiding Seminar Nasional Rekayasa (2024)",
    similarity: 0.84,
    text_snippet: "pendekatan berbasis representasi vektor padat kalimat membuktikan efektivitas tinggi dalam mengenali parafrasa...",
  },
  {
    start: 310,
    end: 450,
    tier: "T3",
    color: "YELLOW",
    source_title: "AI Pattern Indicator",
    similarity: 0.72,
    text_snippet: "Karakteristik teks memiliki keragaman leksikal yang seragam serta variasi panjang kalimat yang konsisten rendah...",
  },
]);

const matchedSources = ref<MatchedSource[]>([
  {
    corpus_doc_id: "corp-01",
    title: "Jurnal Informatika & Sistem Cerdas Vol. 12 (2023)",
    category: "Informatika",
    contribution_pct: 14.5,
  },
  {
    corpus_doc_id: "corp-02",
    title: "Prosiding Seminar Nasional Rekayasa Perangkat Lunak (2024)",
    category: "Teknik Elektro",
    contribution_pct: 18.2,
  },
]);

function handleAnnotationSelected(anno: HeatmapAnnotation) {
  selectedAnnotation.value = anno;
  openDetailModal();
}

function handleExportPdf() {
  showNotification(
    "Mengunduh sertifikat laporan audit terenkripsi dengan QR code...",
    "success",
    "Unduh Dimulai"
  );
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
  </div>
</template>
