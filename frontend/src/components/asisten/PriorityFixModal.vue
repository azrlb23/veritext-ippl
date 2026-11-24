<script setup lang="ts">
import { onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { friendlyChatError } from "../../composables/useAssistant";
import { chatService, type ParaphraseVariation, type PrioritySentenceItem } from "../../services/chatService";

type VariationItem = ParaphraseVariation & { wordOverlapPct: number | null };

const props = defineProps<{ open: boolean; documentId: string; isFree: boolean }>();
const emit = defineEmits<{ (e: "close"): void; (e: "applied"): void }>();
const router = useRouter();

const items = ref<PrioritySentenceItem[]>([]);
const loading = ref(false);
const error = ref("");
const genId = ref<string | null>(null);
const applyKey = ref<string | null>(null);
const variations = ref<Record<string, VariationItem[]>>({});
const applied = ref<Record<string, boolean>>({});
const copiedKey = ref<string | null>(null);
let copyTimer: ReturnType<typeof setTimeout> | null = null;

const BADGES: Record<string, { label: string; cls: string }> = {
  RED: { label: "Kata sama", cls: "bg-[#FEE2E2] text-[#991B1B]" },
  ORANGE: { label: "Makna sama", cls: "bg-[#FFEDD5] text-[#9A3412]" },
  YELLOW: { label: "Pola AI", cls: "bg-[#FEF9C3] text-[#854D0E]" },
};
const badgeOf = (t: string) => BADGES[t] || { label: "Perlu ditinjau", cls: "bg-[#F4F5F6] text-[#4B4757]" };
const pct = (v: number) => Math.round(v > 1 ? v : v * 100);

async function loadItems() {
  if (!props.documentId) return;
  loading.value = true;
  error.value = "";
  variations.value = {};
  applied.value = {};
  try {
    const res = await chatService.getPrioritySentences(props.documentId, 5);
    items.value = (Array.isArray(res) ? res : res.items || []).slice(0, 5);
  } catch (err: any) { error.value = friendlyChatError(err); }
  finally { loading.value = false; }
}

async function generate(item: PrioritySentenceItem) {
  if (props.isFree) { emit("close"); return router.push("/billing"); }
  genId.value = item.sentence_id;
  error.value = "";
  try {
    const res = await chatService.paraphrase(item.sentence_id, "SENTENCE");
    const checked = await Promise.all(res.variations.map(async (v) => {
      const sim = await chatService.checkSimilarity(item.text, v.text).catch(() => null);
      return { ...v, wordOverlapPct: sim ? Math.round(sim.word_overlap_pct) : null };
    }));
    variations.value = { ...variations.value, [item.sentence_id]: checked };
  } catch (err: any) { error.value = friendlyChatError(err); }
  finally { genId.value = null; }
}

async function copyText(key: string, text: string) {
  try {
    await navigator.clipboard.writeText(text);
    copiedKey.value = key;
    if (copyTimer) clearTimeout(copyTimer);
    copyTimer = setTimeout(() => { copiedKey.value = null; }, 1500);
  } catch { error.value = "Gagal menyalin teks ke clipboard."; }
}

async function applyChoice(sentenceId: string, optionId: number, text: string) {
  applyKey.value = `${sentenceId}-${optionId}`;
  error.value = "";
  try {
    await chatService.applyParaphrase(sentenceId, text);
    applied.value = { ...applied.value, [sentenceId]: true };
    emit("applied");
  } catch (err: any) { error.value = friendlyChatError(err); }
  finally { applyKey.value = null; }
}

watch(() => [props.open, props.documentId], ([isOpen]) => { if (isOpen) loadItems(); }, { immediate: true });
onUnmounted(() => { if (copyTimer) clearTimeout(copyTimer); });
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#14111C]/45 p-4 backdrop-blur-[2px]" @click.self="emit('close')" @keydown.esc="emit('close')">
      <div role="dialog" aria-modal="true" aria-labelledby="priority-fix-title" class="flex max-h-[88vh] w-full max-w-2xl flex-col rounded-[32px] bg-white p-6 shadow-float sm:p-8">
        <div class="flex items-start justify-between gap-4 border-b border-[#E8ECEB] pb-4">
          <div>
            <h2 id="priority-fix-title" class="text-[20px] font-semibold tracking-[-0.03em] text-[#14111C]">Perbaiki 5 kalimat prioritas</h2>
            <p class="mt-1 text-[14px] text-[#4B4757]">Buat saran AI, periksa kemiripan kata tersisa, lalu terapkan ke naskah.</p>
          </div>
          <button type="button" aria-label="Tutup dialog" title="Tutup" class="vt-btn-light inline-flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="emit('close')">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>
        <p v-if="error" class="mt-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>
        <div class="mt-4 flex-1 space-y-4 overflow-y-auto no-scrollbar pr-1">
          <p v-if="loading" class="py-10 text-center text-[15px] text-[#4B4757]">Memuat kalimat prioritas...</p>
          <p v-else-if="items.length === 0" class="py-10 text-center text-[15px] text-[#4B4757]">Tidak ada kalimat bermasalah pada naskah ini.</p>
          <article v-for="item in items" :key="item.sentence_id" class="rounded-[24px] border border-[#E8ECEB] bg-white p-4 sm:p-5">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full px-3 py-1 text-[12px] font-semibold" :class="badgeOf(item.match_type).cls">{{ badgeOf(item.match_type).label }}</span>
                <span class="text-[13px] font-medium tabular-nums text-[#5E5A6B]">Skor awal: {{ pct(item.similarity_score) }}%</span>
              </div>
              <span v-if="applied[item.sentence_id]" class="rounded-full bg-[#D1FAE5] px-3 py-1 text-[12px] font-semibold text-[#065F46]">Sudah diterapkan</span>
            </div>
            <p class="mt-2.5 text-[15px] leading-relaxed text-[#14111C]">{{ item.text }}</p>
            <div v-if="!applied[item.sentence_id]" class="mt-3.5">
              <button type="button" :disabled="genId === item.sentence_id" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-5 text-[13.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:opacity-40" @click="generate(item)">
                {{ genId === item.sentence_id ? "Membuat saran..." : "Buat saran AI" }}
              </button>
            </div>
            <ul v-if="variations[item.sentence_id]?.length" class="mt-4 space-y-3 border-t border-[#E8ECEB] pt-4">
              <li v-for="v in variations[item.sentence_id]" :key="v.option_id" class="rounded-[20px] border border-[#E8ECEB] bg-[#F8FAFC] p-4">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="text-[12.5px] font-semibold text-[#4B4757]">{{ v.style }}</span>
                  <span v-if="v.wordOverlapPct !== null" class="rounded-full bg-[#EBF8F6] px-3 py-1 text-[12px] font-semibold tabular-nums text-[#0F766E]">Kemiripan kata tersisa: {{ v.wordOverlapPct }}%</span>
                </div>
                <p class="mt-2 text-[14.5px] leading-relaxed text-[#14111C]">{{ v.text }}</p>
                <div class="mt-3 flex flex-wrap justify-end gap-2">
                  <button type="button" class="vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-4 text-[13px] font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="copyText(`${item.sentence_id}-${v.option_id}`, v.text)">{{ copiedKey === `${item.sentence_id}-${v.option_id}` ? "Tersalin" : "Salin" }}</button>
                  <button type="button" :disabled="Boolean(applyKey) || applied[item.sentence_id]" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[13px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:opacity-40" @click="applyChoice(item.sentence_id, v.option_id, v.text)">{{ applyKey === `${item.sentence_id}-${v.option_id}` ? "Menerapkan..." : "Terapkan ke Naskah" }}</button>
                </div>
              </li>
            </ul>
          </article>
        </div>
      </div>
    </div>
  </Teleport>
</template>
