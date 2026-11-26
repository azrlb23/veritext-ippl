<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { auditService } from "../../services/auditService";
import type { SourcePreviewData } from "../../types";

const INITIAL_LIMIT = 12000;
const props = defineProps<{
  open: boolean;
  reportId: string;
  target: { title?: string; corpus_doc_id?: string; source_url?: string; focusSentence?: string } | null;
}>();
const emit = defineEmits<{ (e: "close"): void }>();

const loading = ref(false);
const error = ref("");
const data = ref<SourcePreviewData | null>(null);
const showFull = ref(false);
const activeIdx = ref<number | null>(null);

const visibleText = computed(() => {
  const raw = data.value?.full_text || "";
  return showFull.value || raw.length <= INITIAL_LIMIT ? raw : raw.slice(0, INITIAL_LIMIT);
});
const isTruncated = computed(() => !showFull.value && (data.value?.full_text.length || 0) > INITIAL_LIMIT);

const textSegments = computed(() => {
  const txt = visibleText.value;
  if (!txt) return [];
  const needles = (data.value?.matched_highlights || [])
    .map((m, idx) => ({ idx, needle: (m.matched_source_text || "").trim() }))
    .filter((x) => x.needle.length >= 16);
  if (!needles.length) return [{ text: txt, matchIdx: null as number | null }];

  const lower = txt.toLowerCase();
  const spans: { start: number; end: number; idx: number }[] = [];
  for (const { idx, needle } of needles) {
    const pos = lower.indexOf(needle.slice(0, 80).toLowerCase());
    if (pos >= 0) spans.push({ start: pos, end: Math.min(txt.length, pos + needle.length), idx });
  }
  spans.sort((a, b) => a.start - b.start);
  const out: { text: string; matchIdx: number | null }[] = [];
  let cur = 0;
  for (const sp of spans) {
    if (sp.start < cur) continue;
    if (sp.start > cur) out.push({ text: txt.slice(cur, sp.start), matchIdx: null });
    out.push({ text: txt.slice(sp.start, sp.end), matchIdx: sp.idx });
    cur = sp.end;
  }
  if (cur < txt.length) out.push({ text: txt.slice(cur), matchIdx: null });
  return out;
});

async function jumpToMatch(idx: number) {
  activeIdx.value = idx;
  if (isTruncated.value) showFull.value = true;
  await nextTick();
  document.querySelector(`[data-preview-match="${idx}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
}

watch(() => [props.open, props.target], async ([isOpen]) => {
  if (!isOpen || !props.target || !props.reportId) return;
  loading.value = true; error.value = ""; data.value = null; showFull.value = false; activeIdx.value = null;
  try {
    data.value = await auditService.getSourcePreview(props.reportId, props.target);
    if (props.target.focusSentence && data.value?.matched_highlights.length) {
      const idx = data.value.matched_highlights.findIndex((m) => m.sentence_text === props.target?.focusSentence);
      await jumpToMatch(idx >= 0 ? idx : 0);
    }
  } catch { error.value = "Isi teks sumber pembanding belum bisa dimuat."; }
  finally { loading.value = false; }
}, { immediate: true });
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[110] flex items-center justify-center bg-[#14111C]/45 p-4 backdrop-blur-[2px]" @click.self="emit('close')" @keydown.esc="emit('close')">
      <div role="dialog" aria-modal="true" aria-labelledby="src-preview-title" class="flex max-h-[88vh] w-full max-w-3xl flex-col rounded-[32px] bg-white p-6 shadow-float sm:p-8">
        <div class="flex items-start justify-between gap-4 border-b border-[#E8ECEB] pb-4">
          <div class="min-w-0">
            <p class="text-[12.5px] font-medium text-[#0F766E]">{{ data?.category || "Pratinjau Sumber Pembanding" }}</p>
            <h2 id="src-preview-title" class="mt-0.5 text-[19px] font-semibold leading-snug tracking-[-0.02em] text-[#14111C]">{{ data?.title || target?.title || "Sumber Pembanding" }}</h2>
          </div>
          <button type="button" aria-label="Tutup pratinjau" class="vt-btn-light inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full" @click="emit('close')">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="mt-4 flex-1 space-y-4 overflow-y-auto pr-1">
          <p v-if="loading" class="py-12 text-center text-[15px] text-[#4B4757]">Memuat isi teks pembanding...</p>
          <p v-else-if="error" class="py-12 text-center text-[15px] text-[#B91C1C]">{{ error }}</p>
          <template v-else-if="data">
            <div v-if="data.matched_highlights.length" class="space-y-2 rounded-2xl border border-[#D5ECE8] bg-[#EBF8F6] p-4">
              <p class="text-[13px] font-semibold text-[#0F766E]">Kalimat naskah yang cocok ({{ data.matched_highlights.length }}) — klik untuk lompat ke posisi sumber</p>
              <div class="flex flex-wrap gap-2">
                <button v-for="(m, idx) in data.matched_highlights.slice(0, 8)" :key="idx" type="button" class="cursor-pointer rounded-full border border-[#CBE6E1] bg-white px-3 py-1.5 text-left text-[12.5px] text-[#14111C] hover:border-[#0F766E]" @click="jumpToMatch(idx)">
                  <span class="font-semibold text-[#0F766E]">#{{ idx + 1 }} ({{ ((m.similarity > 1 ? m.similarity : m.similarity * 100)).toFixed(0) }}%)</span> {{ m.sentence_text.slice(0, 55) }}{{ m.sentence_text.length > 55 ? '...' : '' }}
                </button>
              </div>
            </div>

            <div class="rounded-2xl border border-[#E8ECEB] bg-[#F8FAFC] p-4 sm:p-5">
              <p v-if="!data.full_text" class="text-[14px] italic text-[#5E5A6B]">Teks lengkap tidak tersedia secara langsung dari situs eksternal; gunakan tautan di bawah untuk membuka sumber asli.</p>
              <p v-else class="whitespace-pre-wrap text-[14.5px] leading-[1.75] text-[#14111C]">
                <template v-for="(seg, si) in textSegments" :key="si">
                  <mark v-if="seg.matchIdx !== null" :data-preview-match="seg.matchIdx" class="rounded px-1 py-0.5" :class="activeIdx === seg.matchIdx ? 'bg-[#FDBA74] ring-2 ring-[#0F766E]' : 'bg-[#FEE2E2]'">{{ seg.text }}</mark>
                  <template v-else>{{ seg.text }}</template>
                </template>
              </p>
              <button v-if="isTruncated" type="button" class="mt-4 cursor-pointer text-[13.5px] font-semibold text-[#0F766E] hover:underline" @click="showFull = true">
                Tampilkan seluruh teks ({{ data.full_text.length.toLocaleString('id-ID') }} karakter)
              </button>
            </div>
          </template>
        </div>

        <div v-if="data?.source_url" class="mt-4 flex justify-end border-t border-[#E8ECEB] pt-4">
          <a :href="data.source_url" target="_blank" rel="noopener noreferrer" class="vt-btn-dark inline-flex h-11 items-center rounded-full px-6 text-[14px] font-semibold">Buka sumber asli</a>
        </div>
      </div>
    </div>
  </Teleport>
</template>
