<script setup lang="ts">
import { computed } from "vue";

interface QuickActionItem { id: string; label: string; taskMode: string; prompt: string }
const props = defineProps<{ docCount: number; hasFocusSentence: boolean }>();
const emit = defineEmits<{ (e: "pick", payload: { prompt: string; taskMode: string }): void }>();
const BASE_ACTIONS: QuickActionItem[] = [
  { id: "audit", label: "Bedah hasil audit & prioritas revisi", taskMode: "AUDIT_COACH", prompt: "Bedah hasil audit naskah ini dan jelaskan prioritas kalimat yang paling mendesak untuk direvisi." },
  { id: "citation", label: "Rapikan sitasi & daftar pustaka (APA/IEEE)", taskMode: "CITATION_ASSIST", prompt: "Periksa dan rapikan format sitasi serta daftar pustaka pada naskah ini sesuai gaya APA/IEEE." },
  { id: "ai-style", label: "Perbaiki pola AI agar lebih alami", taskMode: "STYLE_REVIEW", prompt: "Identifikasi bagian yang terdeteksi pola AI pada naskah ini dan beri saran perbaikan agar lebih alami." },
  { id: "eyd", label: "Cek ejaan EYD Edisi V & kalimat efektif", taskMode: "EYD_PROOFREAD", prompt: "Periksa ejaan sesuai EYD Edisi V serta keefektifan kalimat pada naskah ini." },
];

const actions = computed<QuickActionItem[]>(() => {
  const list = [...BASE_ACTIONS];
  if (props.docCount >= 2) {
    list.push({
      id: "compare",
      label: "Bandingkan progres antar-draf naskah",
      taskMode: "DRAFT_COMPARE",
      prompt: "Bandingkan progres revisi antar-draf naskah yang terlampir dan soroti perubahannya.",
    });
  }
  if (props.hasFocusSentence) {
    list.unshift({
      id: "focus",
      label: "Bedah & tulis ulang kalimat terpilih",
      taskMode: "STYLE_REVIEW",
      prompt: "Bedah kalimat audit yang saya pilih ini dan berikan alternatif penulisan ulang yang lebih baik.",
    });
  }
  return list;
});
</script>

<template>
  <div class="mt-6 grid grid-cols-1 gap-2.5 sm:grid-cols-2" role="group" aria-label="Aksi cepat asisten">
    <button
      v-for="item in actions"
      :key="item.id"
      type="button"
      class="vt-btn-light flex min-h-[44px] w-full cursor-pointer items-center justify-between gap-2 rounded-full px-4 py-2 text-left text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
      @click="emit('pick', { prompt: item.prompt, taskMode: item.taskMode })"
    >
      <span class="truncate">{{ item.label }}</span>
      <svg class="h-4 w-4 shrink-0 text-[#0F766E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
    </button>
  </div>
</template>
