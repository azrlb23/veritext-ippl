<script setup lang="ts">
import { computed, onUnmounted, reactive, ref, watch } from "vue";
import { auditService } from "../../services/auditService";
import type { HeatmapAnnotation } from "../../types";

const props = defineProps<{ reportId?: string; text?: string | null; annotations: HeatmapAnnotation[]; selected?: HeatmapAnnotation | null }>();
const emit = defineEmits<{ (e: "select", a: HeatmapAnnotation): void }>();

type Kind = "RED" | "ORANGE" | "YELLOW" | "RESOLVED_GREEN";
const layers = reactive<Record<Kind, boolean>>({ RED: true, ORANGE: true, YELLOW: true, RESOLVED_GREEN: true });
const KINDS: { key: Kind; label: string; bg: string }[] = [
  { key: "RED", label: "Kata sama", bg: "bg-[#FEE2E2]" },
  { key: "ORANGE", label: "Makna sama", bg: "bg-[#FFEDD5]" },
  { key: "YELLOW", label: "Pola AI", bg: "bg-[#FEF9C3]" },
  { key: "RESOLVED_GREEN", label: "Sudah diperbaiki", bg: "bg-[#DCFCE7]" },
];
const mode = ref<"text" | "pdf">("text");
const onlyHighlighted = ref(false);
const page = ref(1);
const pdfUrl = ref("");
const pdfLoading = ref(false);
const pdfError = ref("");

function kindOf(a: HeatmapAnnotation): Kind {
  if (a.color === "RESOLVED_GREEN" || (a as any).match_type === "RESOLVED_GREEN") return "RESOLVED_GREEN";
  if (a.color === "RED" || a.tier === "T1") return "RED";
  if (a.color === "ORANGE" || a.tier === "T2") return "ORANGE";
  return "YELLOW";
}
const bgOf = (a: HeatmapAnnotation) => KINDS.find((k) => k.key === kindOf(a))!.bg;
const hasAiFlag = (a: HeatmapAnnotation) => kindOf(a) === "YELLOW" || Boolean((a as any).ai_flag);
const isAnnoVisible = (a: HeatmapAnnotation) => layers[kindOf(a)] || (layers.YELLOW && hasAiFlag(a));
const activeBgOf = (a: HeatmapAnnotation) => (layers[kindOf(a)] ? bgOf(a) : layers.YELLOW && hasAiFlag(a) ? "bg-[#FEF9C3]" : "");
const isSelected = (a: HeatmapAnnotation) => !!props.selected && props.selected.start === a.start && props.selected.end === a.end;
function viewOf(a: HeatmapAnnotation): HeatmapAnnotation["active_view"] {
  const k = kindOf(a);
  if ((!layers[k] && layers.YELLOW && hasAiFlag(a)) || k === "YELLOW") return "AI";
  return k === "RED" ? "LEXICAL" : k === "ORANGE" ? "SEMANTIC" : "RESOLVED";
}
const pick = (a: HeatmapAnnotation) => emit("select", { ...a, active_view: viewOf(a) });

const paragraphs = computed(() => {
  const raw = props.text || "";
  if (!raw) return [];
  const sorted = [...props.annotations].sort((x, y) => x.start - y.start);
  const out: { slices: { text: string; anno?: HeatmapAnnotation }[]; len: number; hasActive: boolean }[] = [];
  let cursor = 0;
  for (const part of raw.split("\n\n")) {
    const pStart = cursor, pEnd = cursor + part.length;
    cursor = pEnd + 2;
    if (!part.trim()) continue;
    const slices: { text: string; anno?: HeatmapAnnotation }[] = [];
    let pos = pStart, hasActive = false;
    for (const a of sorted) {
      if (a.end <= pStart || a.start >= pEnd) continue;
      const s = Math.max(pos, Math.max(pStart, a.start)), e = Math.min(pEnd, Math.max(s, a.end));
      if (s > pos) slices.push({ text: raw.slice(pos, s) });
      if (e > s) { slices.push({ text: raw.slice(s, e), anno: a }); if (isAnnoVisible(a)) hasActive = true; }
      pos = Math.max(pos, e);
    }
    if (pos < pEnd) slices.push({ text: raw.slice(pos, pEnd) });
    out.push({ slices, len: part.length, hasActive });
  }
  return out;
});

const pages = computed(() => {
  const list = onlyHighlighted.value ? paragraphs.value.filter((p) => p.hasActive) : paragraphs.value;
  const grouped: (typeof list)[] = [];
  let cur: typeof list = [], len = 0;
  for (const p of list) {
    if (cur.length && len + p.len > 1800) { grouped.push(cur); cur = []; len = 0; }
    cur.push(p); len += p.len;
  }
  if (cur.length) grouped.push(cur);
  return grouped;
});
const safePage = computed(() => Math.min(Math.max(1, page.value), Math.max(1, pages.value.length)));
const currentParas = computed(() => pages.value[safePage.value - 1] || []);
const nextHighlightPage = computed(() => {
  const list = pages.value;
  const cur = safePage.value - 1;
  for (let i = cur + 1; i < list.length; i++) if (list[i].some((p) => p.hasActive)) return i + 1;
  for (let i = 0; i < cur; i++) if (list[i].some((p) => p.hasActive)) return i + 1;
  return null;
});

const revokePdf = () => { if (pdfUrl.value) { window.URL.revokeObjectURL(pdfUrl.value); pdfUrl.value = ""; } };
async function loadPdf() {
  if (!props.reportId || pdfUrl.value || pdfLoading.value) return;
  pdfLoading.value = true; pdfError.value = "";
  try { pdfUrl.value = await auditService.fetchAnnotatedPdfPreviewUrl(props.reportId); }
  catch { pdfError.value = "Pratinjau PDF belum bisa dimuat."; }
  finally { pdfLoading.value = false; }
}
function openTab(next: "text" | "pdf") { mode.value = next; if (next === "pdf") void loadPdf(); }
function jumpNext() { if (nextHighlightPage.value) page.value = nextHighlightPage.value; }
watch([() => props.text, onlyHighlighted], () => { page.value = 1; });
watch(() => props.reportId, () => { revokePdf(); if (mode.value === "pdf") void loadPdf(); });
onUnmounted(revokePdf);
</script>

<template>
  <section class="rounded-[32px] border border-[#E8ECEB] bg-white p-5 shadow-float sm:p-8" aria-label="Naskah dengan sorotan">
    <div class="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[#E8ECEB] pb-4">
      <div class="inline-flex rounded-full bg-[#F2F5F4] p-1" role="tablist" aria-label="Mode tampilan naskah">
        <button type="button" role="tab" :aria-selected="mode === 'text'" class="h-11 cursor-pointer rounded-full px-5 text-[14px] font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="mode === 'text' ? 'bg-[#14111C] text-white' : 'text-[#4B4757] hover:text-[#14111C]'" @click="openTab('text')">Teks interaktif</button>
        <button type="button" role="tab" :aria-selected="mode === 'pdf'" class="h-11 cursor-pointer rounded-full px-5 text-[14px] font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="mode === 'pdf' ? 'bg-[#14111C] text-white' : 'text-[#4B4757] hover:text-[#14111C]'" @click="openTab('pdf')">Pratinjau PDF</button>
      </div>
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[13px] text-[#4B4757]">
        <span class="font-medium tabular-nums">{{ annotations.length }} sorotan</span>
        <span v-if="mode === 'text'">Klik kalimat tersorot untuk tulis ulang</span>
      </div>
    </div>

    <template v-if="mode === 'text'">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap gap-2" role="group" aria-label="Saring sorotan">
          <button v-for="k in KINDS" :key="k.key" type="button" :aria-pressed="layers[k.key]" class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="[k.bg, layers[k.key] ? '' : 'opacity-40']" @click="layers[k.key] = !layers[k.key]">{{ k.label }}</button>
        </div>
        <button type="button" :aria-pressed="onlyHighlighted" class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="onlyHighlighted ? 'bg-[#0F766E] text-white' : 'border border-[#D5ECE8] bg-white text-[#14111C] hover:bg-[#EBF8F6]'" @click="onlyHighlighted = !onlyHighlighted">Hanya bagian tersorot</button>
      </div>
      <div class="mt-6 space-y-5 text-[16px] leading-[1.7] tracking-[-0.01em] text-[#14111C]">
        <p v-if="!text" class="py-16 text-center text-[15px] text-[#4B4757]">Teks naskah tidak tersedia untuk ditampilkan.</p>
        <p v-else-if="!currentParas.length" class="py-16 text-center text-[15px] text-[#4B4757]">Tidak ada bagian tersorot pada saringan aktif.</p>
        <p v-else v-for="(p, pi) in currentParas" :key="`${safePage}-${pi}`" class="whitespace-pre-wrap">
          <template v-for="(s, si) in p.slices" :key="si">
            <span v-if="s.anno" role="button" tabindex="0" class="cursor-pointer rounded-[4px] py-[1px] transition-colors box-decoration-clone focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="[activeBgOf(s.anno), isSelected(s.anno) ? 'ring-2 ring-[#14111C]' : '']" @click="pick(s.anno)" @keydown.enter.prevent="pick(s.anno)" @keydown.space.prevent="pick(s.anno)">{{ s.text }}</span>
            <span v-else>{{ s.text }}</span>
          </template>
        </p>
      </div>
      <div v-if="pages.length" class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E8ECEB] pt-4">
        <div class="flex flex-wrap items-center gap-2">
          <button type="button" :disabled="safePage <= 1" class="vt-btn-light h-11 cursor-pointer rounded-full px-5 text-[14px] font-semibold text-[#14111C] disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="page = safePage - 1">Sebelumnya</button>
          <span class="px-2 text-[14px] font-medium tabular-nums text-[#14111C]">Halaman {{ safePage }} dari {{ pages.length }}</span>
          <button type="button" :disabled="safePage >= pages.length" class="vt-btn-light h-11 cursor-pointer rounded-full px-5 text-[14px] font-semibold text-[#14111C] disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="page = safePage + 1">Berikutnya</button>
        </div>
        <button type="button" :disabled="!nextHighlightPage" class="inline-flex h-11 cursor-pointer items-center rounded-full border border-[#D5ECE8] bg-[#EBF8F6] px-5 text-[14px] font-semibold text-[#0F766E] transition-colors hover:bg-[#D5ECE8] disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="jumpNext">Lompat ke sorotan berikutnya</button>
      </div>
    </template>

    <div v-else class="mt-2">
      <p v-if="pdfLoading" class="py-24 text-center text-[15px] text-[#4B4757]">Memuat pratinjau PDF teranotasi...</p>
      <p v-else-if="pdfError" class="py-24 text-center text-[15px] text-[#B91C1C]">{{ pdfError }}</p>
      <iframe v-else-if="pdfUrl" :src="pdfUrl" title="Pratinjau PDF teranotasi" class="h-[740px] w-full rounded-[20px] border border-[#E8ECEB] bg-[#F8FAF9]" />
      <p v-else class="py-24 text-center text-[15px] text-[#4B4757]">Pratinjau PDF belum tersedia untuk laporan ini.</p>
    </div>
  </section>
</template>