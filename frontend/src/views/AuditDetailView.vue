<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { auditService } from "../services/auditService";
import { useNotification } from "../composables/useNotification";
import type { AuditReport, HeatmapAnnotation, MatchedSource } from "../types";
import ScoreHeader from "../components/workspace/ScoreHeader.vue";
import DocumentHighlights from "../components/workspace/DocumentHighlights.vue";
import SourcesPanel from "../components/workspace/SourcesPanel.vue";
import SourcePreviewModal from "../components/workspace/SourcePreviewModal.vue";
import ParaphrasePanel from "../components/workspace/ParaphrasePanel.vue";
import DrawerDetails from "../components/workspace/DrawerDetails.vue";

const route = useRoute();
const { showNotification } = useNotification();
const loading = ref(true);
const exporting = ref(false);
const exportingDoc = ref(false);
const errorMessage = ref("");
const report = ref<AuditReport | null>(null);
const documentId = ref("");
const documentText = ref("");
const annotations = ref<HeatmapAnnotation[]>([]);
const sources = ref<MatchedSource[]>([]);
const selected = ref<HeatmapAnnotation | null>(null);
const drawerOpen = ref(false);
const previewOpen = ref(false);
const previewTarget = ref<{ title?: string; corpus_doc_id?: string; source_url?: string; focusSentence?: string } | null>(null);
const openSourcePreview = (p: { title?: string; corpus_doc_id?: string; source_url?: string; focusSentence?: string }) => { previewTarget.value = p; previewOpen.value = true; };
let timer: ReturnType<typeof setTimeout> | null = null;

async function load(id: string) {
  if (!id) return;
  try {
    const s = await auditService.getStatus(id).catch(() => null);
    if (s?.document_id) documentId.value = s.document_id;
    if (s?.status === "QUEUED" || s?.status === "PROCESSING") {
      timer = setTimeout(() => load(id), s.status === "QUEUED" ? 3000 : 1500);
      return;
    }
    const data = await auditService.getReport(id);
    const prevId = selected.value?.sentence_id;
    report.value = data;
    documentText.value = data.document_text || "";
    annotations.value = data.heatmap_annotations || [];
    sources.value = data.matched_sources || [];
    selected.value = prevId ? annotations.value.find((x) => x.sentence_id === prevId) || null : null;
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || "Laporan belum bisa dimuat.";
  } finally {
    loading.value = false;
  }
}

async function onApplied(ev: { appliedText: string; newCompositeScore?: number }) {
  const a = selected.value;
  if (!a) return;
  a.color = "RESOLVED_GREEN";
  (a as any).match_type = "RESOLVED_GREEN";
  if (a.text_snippet && documentText.value.includes(a.text_snippet)) documentText.value = documentText.value.replace(a.text_snippet, ev.appliedText);
  a.text_snippet = ev.appliedText;
  if (report.value && ev.newCompositeScore !== undefined) report.value.score_composite = ev.newCompositeScore;
  showNotification("Kalimat baru sudah dipakai di naskah.", "success");
  await load(route.params.id as string);
}

async function download() {
  if (!report.value) return;
  exporting.value = true;
  try {
    await auditService.downloadPdfReport(report.value.id, report.value.document_title || "Naskah");
    showNotification("Sertifikat PDF diunduh.", "success");
  } catch {
    showNotification("Sertifikat belum bisa diunduh.", "error");
  } finally {
    exporting.value = false;
  }
}

async function downloadDoc(fmt: "docx" | "pdf") {
  if (!report.value) return;
  exportingDoc.value = true;
  try {
    await auditService.downloadRevisedDocument(report.value.id, fmt, report.value.document_title || "Naskah");
    showNotification(`Naskah revisi ${fmt.toUpperCase()} diunduh.`, "success");
  } catch {
    showNotification("Naskah revisi belum bisa diunduh.", "error");
  } finally {
    exportingDoc.value = false;
  }
}

onMounted(() => load(route.params.id as string));
onUnmounted(() => { if (timer) clearTimeout(timer); });
watch(() => route.params.id, (id) => {
  if (timer) { clearTimeout(timer); timer = null; }
  drawerOpen.value = false;
  if (id) void load(id as string);
});
</script>

<template>
  <div class="mx-auto max-w-[1360px] px-4 pb-24 pt-6 font-sans sm:px-6 sm:pt-10">
    <p v-if="loading" class="py-24 text-center text-[16px] text-[#5E5A6B]">Memuat hasil pemeriksaan...</p>
    <div v-else-if="errorMessage || !report" class="mx-auto max-w-md rounded-[32px] border border-[#E8ECEB] bg-white p-8 text-center shadow-float">
      <h1 class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Laporan tidak ditemukan</h1>
      <p class="mt-2 text-[15px] text-[#4B4757]">{{ errorMessage || "Naskah tidak ada atau sudah dihapus." }}</p>
      <router-link to="/riwayat" class="vt-btn-dark mt-6 inline-flex h-12 cursor-pointer items-center rounded-full px-7 text-[15px] font-semibold">Kembali ke Riwayat</router-link>
    </div>
    <div v-else class="space-y-6">
      <ScoreHeader :title="report.document_title" :composite="report.score_composite ?? 0" :lexical="report.score_lexical" :semantic="report.score_semantic" :stylometric="report.score_stylometric" :exporting="exporting" :exporting-doc="exportingDoc" @download="download" @download-doc="downloadDoc" />
      <div class="flex flex-wrap items-center justify-end gap-3">
        <router-link :to="documentId ? `/asisten?doc=${documentId}` : '/asisten'" class="vt-btn-light inline-flex h-11 cursor-pointer items-center gap-2 rounded-full px-6 text-[14px] font-semibold text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]">
          <svg class="h-4 w-4 text-[#0F766E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
          Tanya Asisten AI tentang naskah ini
        </router-link>
      </div>
      <DocumentHighlights :report-id="report.id" :text="documentText" :annotations="annotations" :selected="selected" @select="(a) => { selected = a; drawerOpen = true; }" />
      <SourcesPanel :sources="sources" :annotations="annotations" @select-annotation="(a) => { selected = a; drawerOpen = true; }" @preview-source="openSourcePreview" />
      <SourcePreviewModal :open="previewOpen" :report-id="report.id" :target="previewTarget" @close="previewOpen = false" />
    </div>

    <Teleport to="body">
      <div v-if="drawerOpen && selected" class="fixed inset-0 z-[100] flex bg-[#14111C]/25 backdrop-blur-[2px]" role="dialog" aria-modal="true" aria-label="Detail dan Tulis ulang" @click.self="drawerOpen = false" @keydown.esc="drawerOpen = false">
        <div class="ml-auto flex h-full w-full max-w-md flex-col overflow-y-auto bg-white p-6 shadow-float sm:p-8">
          <div class="flex items-center justify-between gap-4 border-b border-[#E8ECEB] pb-4">
            <h2 class="text-[20px] font-semibold tracking-[-0.02em] text-[#14111C]">Detail &amp; Tulis ulang</h2>
            <button type="button" aria-label="Tutup" title="Tutup" class="vt-btn-light inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="drawerOpen = false">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
            </button>
          </div>
          <DrawerDetails :selected="selected" @preview-source="openSourcePreview" />
          <div class="mt-5 flex-1"><ParaphrasePanel :selected="selected" @applied="onApplied" /></div>
          <div class="mt-6 border-t border-[#E8ECEB] pt-5">
            <router-link :to="documentId ? `/asisten?doc=${documentId}` : '/asisten'" class="vt-btn-light inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-full px-5 text-[14px] font-semibold text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]">Diskusikan lebih lanjut di Asisten AI</router-link>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
