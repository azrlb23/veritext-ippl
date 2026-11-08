<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { auditService } from "../services/auditService";
import { useNotification } from "../composables/useNotification";
import type { AuditReport, HeatmapAnnotation, MatchedSource } from "../types";
import TierLegend from "../components/TierLegend.vue";
import HeatmapViewer from "../components/HeatmapViewer.vue";
import TopSummaryBar from "../components/workspace/TopSummaryBar.vue";
import MatchedSourcesTab from "../components/workspace/MatchedSourcesTab.vue";
import AiAssistantTab from "../components/workspace/AiAssistantTab.vue";

const route = useRoute();
const { showNotification } = useNotification();
const isLoading = ref(true);
const isExporting = ref(false);
const errorMessage = ref("");
const report = ref<AuditReport | null>(null);
const annotations = ref<HeatmapAnnotation[]>([]);
const matchedSources = ref<MatchedSource[]>([]);
const documentText = ref("");
const selectedSentence = ref<HeatmapAnnotation | null>(null);
const activeTab = ref<"sources" | "ai">("sources");
let pollTimer: ReturnType<typeof setTimeout> | null = null;

async function fetchReportData(id: string) {
  if (!id) return;
  try {
    const s = await auditService.getStatus(id).catch(() => null);
    if (s?.status === "QUEUED") { pollTimer = setTimeout(() => fetchReportData(id), 3000); return; }
    if (s?.status === "PROCESSING") { pollTimer = setTimeout(() => fetchReportData(id), 1500); return; }
    const data = await auditService.getReport(id);
    if (data) {
      report.value = data;
      documentText.value = data.document_text || "";
      annotations.value = data.heatmap_annotations || [];
      matchedSources.value = data.matched_sources || [];
      if (annotations.value.length > 0) selectedSentence.value = annotations.value[0];
    }
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || err?.message || "Gagal memuat laporan audit.";
  } finally {
    isLoading.value = false;
  }
}

function handleParaphraseApplied(ev: { appliedText: string; newCompositeScore?: number }) {
  if (!selectedSentence.value) return;
  selectedSentence.value.color = "RESOLVED_GREEN";
  (selectedSentence.value as any).match_type = "RESOLVED_GREEN";
  if (selectedSentence.value.text_snippet && documentText.value.includes(selectedSentence.value.text_snippet)) {
    documentText.value = documentText.value.replace(selectedSentence.value.text_snippet, ev.appliedText);
  }
  selectedSentence.value.text_snippet = ev.appliedText;
  if (report.value && ev.newCompositeScore !== undefined) report.value.score_composite = ev.newCompositeScore;
  showNotification("Parafrase berhasil diterapkan ke naskah.", "success", "Berhasil");
}

async function handleDownloadPdf() {
  if (!report.value) return;
  isExporting.value = true;
  try {
    await auditService.downloadPdfReport(report.value.id, report.value.document_title || "Naskah");
    showNotification("Sertifikat PDF resmi berhasil diunduh.", "success", "Unduh Berhasil");
  } catch (err: any) {
    showNotification(err?.message || "Gagal mengunduh sertifikat PDF.", "error", "Unduh Gagal");
  } finally {
    isExporting.value = false;
  }
}

onMounted(() => fetchReportData(route.params.id as string));
onUnmounted(() => { if (pollTimer) clearTimeout(pollTimer); });
watch(() => route.params.id, (newId) => { if (newId) fetchReportData(newId as string); });
</script>

<template>
  <div class="min-h-screen bg-[#F4F6F9] p-4 sm:p-6 lg:p-8 space-y-6">
    <div v-if="isLoading" class="text-center py-20 text-gray-500 animate-pulse text-sm">Memuat naskah dan hasil audit...</div>
    <div v-else-if="errorMessage || !report" class="max-w-md mx-auto my-16 bg-white rounded-2xl p-6 text-center border border-gray-200 shadow-sm space-y-3">
      <h2 class="text-base font-bold text-gray-900">Laporan Tidak Ditemukan</h2>
      <p class="text-xs text-gray-500">{{ errorMessage || "Naskah tidak ditemukan atau telah dihapus." }}</p>
      <router-link to="/dashboard" class="inline-block px-4 py-2 bg-[#1560BD] text-white text-xs font-semibold rounded-xl">Kembali ke Dashboard</router-link>
    </div>
    <div v-else class="max-w-[1600px] mx-auto space-y-5">
      <TopSummaryBar
        :documentTitle="report.document_title" :scoreComposite="report.score_composite ?? 0"
        :scoreLexical="report.score_lexical" :scoreSemantic="report.score_semantic"
        :scoreStylometric="report.score_stylometric" :isExporting="isExporting" @download-pdf="handleDownloadPdf"
      />
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        <section class="lg:col-span-7 space-y-4">
          <TierLegend />
          <HeatmapViewer :text="documentText" :annotations="annotations" :selectedAnnotation="selectedSentence" @select-sentence="s => selectedSentence = s" />
        </section>
        <aside class="lg:col-span-5 space-y-4">
          <div class="bg-white border border-[#E4E8F0] rounded-2xl p-1.5 flex gap-1 shadow-sm">
            <button type="button" @click="activeTab = 'sources'" class="flex-1 py-2 text-xs font-semibold rounded-xl transition-all" :class="activeTab === 'sources' ? 'bg-[#1560BD] text-white shadow-xs' : 'text-gray-600'">1. Sumber Kemiripan & Diff</button>
            <button type="button" @click="activeTab = 'ai'" class="flex-1 py-2 text-xs font-semibold rounded-xl transition-all" :class="activeTab === 'ai' ? 'bg-[#1560BD] text-white shadow-xs' : 'text-gray-600'">2. AI Asisten & Parafrase 3-Mode</button>
          </div>
          <MatchedSourcesTab v-if="activeTab === 'sources'" :selectedSentence="selectedSentence" :matchedSources="matchedSources" @request-paraphrase="s => { selectedSentence = s; activeTab = 'ai'; }" />
          <AiAssistantTab v-else :documentId="report.audit_task_id || report.id" :selectedSentence="selectedSentence" @paraphrase-applied="handleParaphraseApplied" />
        </aside>
      </div>
    </div>
  </div>
</template>
