<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import type { HeatmapAnnotation } from "../../types";
import { chatService, type ParaphraseVariation } from "../../services/chatService";
import { friendlyChatError } from "../../composables/useAssistant";
import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const isFree = computed(() => authStore.role === "FREE");

const props = defineProps<{ selected?: HeatmapAnnotation | null }>();
const emit = defineEmits<{ (e: "applied", d: { appliedText: string; newCompositeScore?: number }): void }>();

type Mode = "SENTENCE" | "PARAGRAPH" | "FULL_PAGE";
const MODES: { key: Mode; label: string }[] = [
  { key: "SENTENCE", label: "Kalimat" },
  { key: "PARAGRAPH", label: "Paragraf" },
  { key: "FULL_PAGE", label: "Halaman" },
];
const mode = ref<Mode>("SENTENCE");
const busy = ref(false);
const applying = ref(false);
const error = ref("");
const variations = ref<ParaphraseVariation[]>([]);
const copiedId = ref<string | number | null>(null);
let copyTimer: ReturnType<typeof setTimeout> | null = null;

async function copyVariation(id: string | number, text: string) {
  try {
    await navigator.clipboard.writeText(text);
    copiedId.value = id;
    if (copyTimer) clearTimeout(copyTimer);
    copyTimer = setTimeout(() => { copiedId.value = null; }, 1800);
  } catch {
    error.value = "Gagal menyalin teks ke clipboard.";
  }
}

async function generate() {
  if (isFree.value) return router.push("/billing");
  if (!props.selected?.sentence_id) return;
  busy.value = true;
  error.value = "";
  variations.value = [];
  try {
    variations.value = (await chatService.paraphrase(props.selected.sentence_id, mode.value)).variations;
    void authStore.fetchProfile();
  } catch (err: any) {
    error.value = friendlyChatError(err);
  } finally {
    busy.value = false;
  }
}

async function apply(text: string) {
  if (!props.selected?.sentence_id) return;
  applying.value = true;
  try {
    const res = await chatService.applyParaphrase(props.selected.sentence_id, text);
    emit("applied", { appliedText: res.current_text || text, newCompositeScore: res.new_composite_score });
    variations.value = [];
  } catch (err: any) {
    error.value = friendlyChatError(err);
  } finally {
    applying.value = false;
  }
}

onUnmounted(() => { if (copyTimer) clearTimeout(copyTimer); });
</script>

<template>
  <div>
    <div class="grid grid-cols-3 gap-1 rounded-full bg-[#F4F5F6] p-1" role="tablist" aria-label="Cakupan tulis ulang">
      <button v-for="m in MODES" :key="m.key" type="button" role="tab" :aria-selected="mode === m.key" class="inline-flex h-11 cursor-pointer items-center justify-center rounded-full text-[14px] font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" :class="mode === m.key ? 'bg-white text-[#14111C] shadow-lift' : 'text-[#5E5A6B] hover:text-[#14111C]'" @click="mode = m.key">{{ m.label }}</button>
    </div>

    <p v-if="!selected" class="py-10 text-center text-[15px] text-[#5E5A6B]">Pilih kalimat yang tersorot di naskah, lalu minta asisten menulis ulang.</p>
    <template v-else>
      <button type="button" :disabled="isFree ? false : busy || !selected.sentence_id" class="vt-btn-dark mt-5 inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:opacity-40" @click="generate">{{ isFree ? "Aktifkan Premium untuk Tulis Ulang" : busy ? "Menulis ulang..." : "Buat 3 pilihan kalimat" }}</button>
    </template>
    <p v-if="error" class="mt-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>

    <ul v-if="variations.length" class="mt-5 space-y-3">
      <li v-for="v in variations" :key="v.option_id" class="rounded-[20px] border border-[#E8ECEB] bg-white p-5">
        <div class="flex items-center justify-between gap-2">
          <p class="text-[13px] font-medium text-[#5E5A6B]">{{ v.style }}</p>
          <p class="text-[13px] text-[#5E5A6B]">Skor akhir <span class="font-semibold tabular-nums text-[#047857]">{{ v.predicted_score.toFixed(1).replace(".", ",") }}%</span></p>
        </div>
        <p class="mt-2 text-[15.5px] leading-relaxed text-[#14111C]">{{ v.text }}</p>
        <div class="mt-4 flex flex-wrap items-center justify-end gap-2">
          <button type="button" class="vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2" @click="copyVariation(v.option_id, v.text)">{{ copiedId === v.option_id ? "Tersalin" : "Salin" }}</button>
          <button type="button" :disabled="applying" class="vt-btn-dark inline-flex h-10 cursor-pointer items-center rounded-full px-5 text-[13.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:opacity-40" @click="apply(v.text)">Pakai di naskah</button>
        </div>
      </li>
    </ul>
  </div>
</template>
