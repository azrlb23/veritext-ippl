<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { auditService } from "../services/auditService";
import { useNotification } from "../composables/useNotification";
import type { AuditReport, HeatmapAnnotation, MatchedSource } from "../types";
import ScoreHeader from "../components/workspace/ScoreHeader.vue";
import DocumentHighlights from "../components/workspace/DocumentHighlights.vue";
import SourcesPanel from "../components/workspace/SourcesPanel.vue";
import ParaphrasePanel from "../components/workspace/ParaphrasePanel.vue";
import ChatPanel from "../components/workspace/ChatPanel.vue";

const route = useRoute();
const { showNotification } = useNotification();
const loading = ref(true);
const exporting = ref(false);
const errorMessage = ref("");
const report = ref<AuditReport | null>(null);
const documentId = ref("");
const documentText = ref("");
const annotations = ref<HeatmapAnnotation[]>([]);
const sources = ref<MatchedSource[]>([]);
const selected = ref<HeatmapAnnotation | null>(null);
const tab = ref<"sources" | "rewrite" | "ask">("sources");
let timer: ReturnType<typeof setTimeout> | null = null;

const TABS = [
  { key: "sources", label: "Sumber" },
  { key: "rewrite", label: "Tulis ulang" },
  { key: "ask", label: "Tanya" },
] as const;

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
    report.value = data;
    documentText.value = data.document_text || "";
    annotations.value = data.heatmap_annotations || [];
    sources.value = data.matched_sources || [];
    selected.value = annotations.value[0] ?? null;
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || "Laporan belum bisa dimuat.";
  } finally {
    loading.value = false;
  }
}

function onApplied(ev: { appliedText: string; newCompositeScore?: number }) {
  const a = selected.value;
  if (!a) return;
  a.color = "RESOLVED_GREEN";
  (a as any).match_type = "RESOLVED_GREEN";
  if (a.text_snippet && documentText.value.includes(a.text_snippet)) documentText.value = documentText.value.replace(a.text_snippet, ev.appliedText);
  a.text_snippet = ev.appliedText;
  if (report.value && ev.newCompositeScore !== undefined) report.value.score_composite = ev.newCompositeScore;
  showNotification("Kalimat baru sudah dipakai di naskah.", "success");
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

onMounted(() => load(route.params.id as string));
onUnmounted(() => { if (timer) clearTimeout(timer); });
watch(() => route.params.id, (id) => id && load(id as string));
</script>

<template>
  <div class="mx-auto max-w-[1280px] px-4 pb-24 pt-6 font-sans sm:px-6 sm:pt-10">
    <p v-if="loading" class="py-24 text-center text-[16px] text-[#5E5A6B]">Memuat hasil pemeriksaan...</p>
    <div v-else-if="errorMessage || !report" class="mx-auto max-w-md rounded-[32px] bg-white p-8 text-center shadow-float">
      <h1 class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Laporan tidak ditemukan</h1>
      <p class="mt-2 text-[15px] text-[#4B4757]">{{ errorMessage || "Naskah tidak ada atau sudah dihapus." }}</p>
      <router-link to="/riwayat" class="mt-6 inline-flex h-12 cursor-pointer items-center rounded-full bg-[#14111C] px-7 text-[15px] font-semibold text-white shadow-btn-dark">Kembali ke Riwayat</router-link>
    </div>
    <div v-else class="space-y-6">
      <ScoreHeader :title="report.document_title" :composite="report.score_composite ?? 0" :lexical="report.score_lexical" :semantic="report.score_semantic" :stylometric="report.score_stylometric" :exporting="exporting" @download="download" />
      <div class="grid items-start gap-6 lg:grid-cols-[1.35fr_1fr]">
        <DocumentHighlights :text="documentText" :annotations="annotations" :selected="selected" @select="(a) => (selected = a)" />
        <aside class="rounded-[32px] bg-white p-5 shadow-float sm:p-7 lg:sticky lg:top-24">
          <div class="mb-5 grid grid-cols-3 gap-1 rounded-full bg-[#F3EEFA] p-1" role="tablist">
            <button v-for="t in TABS" :key="t.key" type="button" role="tab" :aria-selected="tab === t.key" class="inline-flex h-11 cursor-pointer items-center justify-center rounded-full text-[14px] font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]" :class="tab === t.key ? 'bg-white text-[#14111C] shadow-lift' : 'text-[#5E5A6B]'" @click="tab = t.key">{{ t.label }}</button>
          </div>
          <SourcesPanel v-if="tab === 'sources'" :selected="selected" :sources="sources" @rewrite="(a) => { selected = a; tab = 'rewrite'; }" />
          <ParaphrasePanel v-else-if="tab === 'rewrite'" :selected="selected" @applied="onApplied" />
          <ChatPanel v-else :document-id="documentId" :selected="selected" />
        </aside>
      </div>
    </div>
  </div>
</template>
