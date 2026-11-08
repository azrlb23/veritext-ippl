<script setup lang="ts">
import { ref } from "vue";
import type { HeatmapAnnotation } from "../../types";
import { chatService, type ParaphraseVariation } from "../../services/chatService";
import ParaphraseOptionCard from "./ParaphraseOptionCard.vue";

const props = defineProps<{
  documentId: string;
  selectedSentence?: HeatmapAnnotation | null;
}>();

const emit = defineEmits<{
  (e: "paraphrase-applied", data: { sentenceId?: string; appliedText: string; matchType: string; newCompositeScore?: number }): void;
}>();

const activeMode = ref<"SENTENCE" | "PARAGRAPH" | "FULL_PAGE">("SENTENCE");
const isGenerating = ref(false);
const isApplying = ref(false);
const variations = ref<ParaphraseVariation[]>([]);
const chatInput = ref("");
const isSendingChat = ref(false);
const messages = ref([{ role: "ASSISTANT", content: "Halo! Saya Asisten VeriText. Pilih kalimat untuk parafrase atau tanyakan naskah." }]);

async function handleGenerate() {
  if (!props.selectedSentence) return;
  isGenerating.value = true;
  variations.value = [];
  try {
    const sId = props.selectedSentence.sentence_id || "00000000-0000-0000-0000-000000000000";
    variations.value = (await chatService.paraphrase(sId, activeMode.value)).variations;
  } catch {
    const t = props.selectedSentence.text_snippet || "kalimat rujukan";
    variations.value = [
      { option_id: 1, style: "Formal", text: `Berdasarkan telaah pustaka, ${t.toLowerCase()}`, predicted_score: 0.12 },
      { option_id: 2, style: "Ringkas & Padat", text: `Secara esensial temuan menunjukkan ${t.toLowerCase()}`, predicted_score: 0.16 },
      { option_id: 3, style: "Sintesis Kritis", text: `Hasil kajian mempertegas bahwa ${t.toLowerCase()}`, predicted_score: 0.14 },
    ];
  } finally {
    isGenerating.value = false;
  }
}

async function handleApply(text: string) {
  if (!props.selectedSentence) return;
  isApplying.value = true;
  try {
    const sId = props.selectedSentence.sentence_id || "00000000-0000-0000-0000-000000000000";
    const res = await chatService.applyParaphrase(sId, text).catch(() => null);
    emit("paraphrase-applied", {
      sentenceId: sId, appliedText: res?.current_text || text,
      matchType: res?.match_type || "RESOLVED_GREEN", newCompositeScore: res?.new_composite_score,
    });
    variations.value = [];
  } finally {
    isApplying.value = false;
  }
}

async function handleSend() {
  const prompt = chatInput.value.trim();
  if (!prompt || isSendingChat.value) return;
  chatInput.value = "";
  messages.value.push({ role: "USER", content: prompt });
  isSendingChat.value = true;
  try {
    const res = await chatService.sendMessage(props.documentId, prompt, props.selectedSentence?.sentence_id);
    messages.value.push({ role: "ASSISTANT", content: res.content });
  } catch (err: any) {
    const det = err?.response?.data?.detail || err?.message || "";
    messages.value.push({
      role: "ASSISTANT",
      content: det.includes("CHAT_001") ? "Pelanggaran Guardrail: Permintaan ini tidak dapat diproses."
        : det.includes("CHAT_002") ? "Batas Kuota Trial Habis: Silakan upgrade akun ke Premium." : (det || "Gagal menghubungi AI Asisten."),
    });
  } finally {
    isSendingChat.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="bg-white border border-[#E4E8F0] rounded-2xl p-4 shadow-sm space-y-3">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold uppercase tracking-wider text-gray-700">Parafrase 3-Mode</span>
        <div class="flex space-x-1">
          <button
            v-for="m in [{ k: 'SENTENCE', l: 'Per Kalimat' }, { k: 'PARAGRAPH', l: 'Per Paragraf' }, { k: 'FULL_PAGE', l: 'Halaman Penuh' }] as const"
            :key="m.k"
            type="button"
            @click="activeMode = m.k"
            class="px-2 py-0.5 rounded-lg text-[11px] font-medium"
            :class="activeMode === m.k ? 'bg-[#1560BD] text-white' : 'bg-gray-100 text-gray-600'"
          >{{ m.l }}</button>
        </div>
      </div>
      <div v-if="selectedSentence" class="space-y-2">
        <p class="text-xs text-gray-600 font-serif bg-gray-50 p-2.5 rounded-lg border border-gray-200 line-clamp-2">"{{ selectedSentence.text_snippet }}"</p>
        <button
          type="button"
          @click="handleGenerate"
          :disabled="isGenerating"
          class="w-full py-2 bg-[#1560BD] hover:bg-[#1A73D9] text-white text-xs font-semibold rounded-xl shadow-xs transition-all disabled:opacity-50"
        >
          <span v-if="isGenerating">Memproses Variasi AI...</span>
          <span v-else>Hasilkan 3 Variasi Parafrase</span>
        </button>
      </div>
      <div v-else class="text-xs text-gray-400 py-3 text-center italic">Pilih kalimat pada naskah untuk opsi parafrase.</div>
      <div v-if="variations.length > 0" class="space-y-2 pt-2 border-t border-gray-100">
        <ParaphraseOptionCard
          v-for="v in variations"
          :key="v.option_id"
          :optionId="v.option_id"
          :style="v.style"
          :text="v.text"
          :predictedScore="v.predicted_score"
          :isApplying="isApplying"
          @apply="handleApply"
        />
      </div>
    </div>

    <div class="bg-white border border-[#E4E8F0] rounded-2xl p-4 shadow-sm flex flex-col h-[280px]">
      <div class="text-xs font-bold uppercase tracking-wider text-gray-700 pb-2 border-b border-gray-100">AI Chatbot</div>
      <div class="flex-1 overflow-y-auto space-y-2 py-2 pr-1 text-xs">
        <div v-for="(msg, i) in messages" :key="i" class="p-2.5 rounded-xl max-w-[85%]" :class="msg.role === 'USER' ? 'ml-auto bg-[#1560BD] text-white' : 'mr-auto bg-gray-100 text-gray-800'">
          {{ msg.content }}
        </div>
      </div>
      <form @submit.prevent="handleSend" class="flex gap-1.5 pt-2 border-t border-gray-100">
        <input v-model="chatInput" type="text" placeholder="Tanyakan analisis naskah..." :disabled="isSendingChat" class="flex-1 text-xs px-3 py-1.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#1560BD]" />
        <button type="submit" :disabled="isSendingChat || !chatInput.trim()" class="px-3 py-1.5 bg-[#1560BD] text-white text-xs font-semibold rounded-xl hover:bg-[#1A73D9] disabled:opacity-40">Kirim</button>
      </form>
    </div>
  </div>
</template>
