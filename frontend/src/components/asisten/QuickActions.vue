<script setup lang="ts">
import { computed } from "vue";

interface QuickActionItem { id: string; label: string; taskMode: string; prompt: string; requiresDoc?: boolean }
const props = defineProps<{ docCount: number; hasFocusSentence: boolean; hasDocuments?: boolean }>();
const emit = defineEmits<{ (e: "pick", payload: { prompt: string; taskMode: string }): void; (e: "attach-latest"): void }>();
const BASE_ACTIONS: QuickActionItem[] = [
  { id: "audit", label: "Bedah hasil audit & prioritas revisi", taskMode: "AUDIT_COACH", prompt: "Bedah hasil audit naskah ini dan jelaskan prioritas kalimat yang paling mendesak untuk direvisi.", requiresDoc: true },
  { id: "citation", label: "Rapikan sitasi & daftar pustaka (APA/IEEE)", taskMode: "CITATION_ASSIST", prompt: "Periksa dan rapikan format sitasi serta daftar pustaka pada naskah ini sesuai gaya APA/IEEE.", requiresDoc: true },
  { id: "ai-style", label: "Perbaiki pola AI agar lebih alami", taskMode: "STYLE_REVIEW", prompt: "Identifikasi bagian yang terdeteksi pola AI pada naskah ini dan beri saran perbaikan agar lebih alami.", requiresDoc: true },
  { id: "eyd", label: "Cek ejaan EYD Edisi V & kalimat efektif", taskMode: "EYD_PROOFREAD", prompt: "Periksa ejaan sesuai EYD Edisi V serta keefektifan kalimat pada naskah ini.", requiresDoc: true },
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
  <div class="mt-6 space-y-3">
    <div v-if="docCount === 0" class="flex flex-wrap items-center justify-between gap-2 border-l-2 border-[#0F766E] pl-3 text-[13px] text-[#4B4757]">
      <span>Lampirkan naskah terlebih dahulu agar aksi berbasis laporan audit aktif.</span>
      <button
        v-if="hasDocuments"
        type="button"
        class="inline-flex min-h-[44px] cursor-pointer items-center font-semibold text-[#0F766E] underline underline-offset-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        @click="emit('attach-latest')"
      >Lampirkan naskah terbaru</button>
    </div>
    <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2" role="group" aria-label="Aksi cepat asisten">
      <button
        v-for="item in actions"
        :key="item.id"
        type="button"
        :disabled="Boolean(item.requiresDoc && docCount === 0)"
        :title="item.requiresDoc && docCount === 0 ? 'Lampirkan naskah terlebih dahulu' : item.label"
        class="vt-btn-light flex min-h-[44px] w-full cursor-pointer items-center justify-between gap-2 rounded-full px-4 py-2 text-left text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-45"
        @click="emit('pick', { prompt: item.prompt, taskMode: item.taskMode })"
      >
        <span class="truncate">{{ item.label }}</span>
        <svg class="h-4 w-4 shrink-0 text-[#0F766E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
      </button>
    </div>
  </div>
</template>
