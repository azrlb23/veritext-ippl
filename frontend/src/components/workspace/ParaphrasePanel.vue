<script setup lang="ts">
import { ref } from "vue";
import type { HeatmapAnnotation } from "../../types";
import { chatService, type ParaphraseVariation } from "../../services/chatService";
import { friendlyChatError } from "../../composables/useAssistant";

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

async function generate() {
  if (!props.selected?.sentence_id) return;
  busy.value = true;
  error.value = "";
  variations.value = [];
  try {
    variations.value = (await chatService.paraphrase(props.selected.sentence_id, mode.value)).variations;
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
</script>

<template>
  <div>
    <div class="grid grid-cols-3 gap-1 rounded-full bg-[#F3EEFA] p-1" role="tablist" aria-label="Cakupan tulis ulang">
      <button v-for="m in MODES" :key="m.key" type="button" role="tab" :aria-selected="mode === m.key" class="inline-flex h-11 cursor-pointer items-center justify-center rounded-full text-[14px] font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]" :class="mode === m.key ? 'bg-white text-[#14111C] shadow-lift' : 'text-[#5E5A6B]'" @click="mode = m.key">{{ m.label }}</button>
    </div>

    <p v-if="!selected" class="py-10 text-center text-[15px] text-[#5E5A6B]">Pilih kalimat yang tersorot di naskah, lalu minta asisten menulis ulang.</p>
    <template v-else>
      <p class="mt-5 rounded-[20px] bg-[#F3EEFA] p-4 text-[15px] leading-relaxed text-[#14111C]">{{ selected.text_snippet }}</p>
      <button type="button" :disabled="busy || !selected.sentence_id" class="mt-4 inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:opacity-40" @click="generate">{{ busy ? "Menulis ulang..." : "Buat 3 pilihan kalimat" }}</button>
    </template>
    <p v-if="error" class="mt-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>

    <ul v-if="variations.length" class="mt-5 space-y-3">
      <li v-for="v in variations" :key="v.option_id" class="rounded-[24px] bg-[#F3EEFA] p-5">
        <p class="text-[13px] font-medium text-[#5E5A6B]">{{ v.style }}</p>
        <p class="mt-1 text-[15.5px] leading-relaxed text-[#14111C]">{{ v.text }}</p>
        <div class="mt-4 flex items-center justify-between gap-3">
          <p class="text-[14px] text-[#5E5A6B]">Perkiraan kemiripan <span class="font-semibold tabular-nums text-[#14111C]">{{ v.predicted_score.toFixed(1).replace(".", ",") }}%</span></p>
          <button type="button" :disabled="applying" class="inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-5 text-[14px] font-semibold text-white shadow-btn-dark focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:opacity-40" @click="apply(v.text)">Pakai</button>
        </div>
      </li>
    </ul>
  </div>
</template>
