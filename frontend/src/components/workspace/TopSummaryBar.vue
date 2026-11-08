<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";

const props = defineProps<{
  documentTitle?: string | null;
  scoreComposite: number;
  scoreLexical?: number | null;
  scoreSemantic?: number | null;
  scoreStylometric?: number | null;
  isExporting?: boolean;
}>();

const emit = defineEmits<{
  (e: "download-pdf"): void;
}>();

const router = useRouter();
const authStore = useAuthStore();

const severity = computed(() => {
  const s = props.scoreComposite ?? 0;
  if (s <= 20) return { label: "Lolos (Aman)", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" };
  if (s <= 40) return { label: "Tinjau (Moderat)", cls: "bg-amber-50 text-amber-700 border-amber-200" };
  return { label: "Tinjau (Tinggi)", cls: "bg-rose-50 text-rose-700 border-rose-200" };
});

const isFreeUser = computed(() => {
  const role = (authStore.role || "FREE").toUpperCase();
  return role === "FREE";
});

const quotaBadge = computed(() => {
  const trial = authStore.user?.ai_trial_remaining ?? 0;
  if (trial > 0) return { label: `Trial AI: ${trial}x`, cls: "bg-indigo-50 text-indigo-700 border-indigo-200" };
  return { label: `Saldo: ${authStore.tokenBalance} Token`, cls: "bg-sky-50 text-sky-700 border-sky-200" };
});

function handleDownloadPdf() {
  if (isFreeUser.value) {
    router.push("/billing");
    return;
  }
  emit("download-pdf");
}
</script>

<template>
  <header class="bg-white border border-[#E4E8F0] rounded-2xl p-4 shadow-sm space-y-3 sm:space-y-0 sm:flex sm:items-center sm:justify-between sm:gap-4">
    <div class="flex items-center space-x-3 min-w-0">
      <router-link
        to="/dashboard"
        class="inline-flex items-center justify-center w-9 h-9 rounded-xl border border-gray-200 bg-gray-50 text-gray-600 hover:bg-gray-100 transition-colors flex-shrink-0"
        title="Kembali ke Dashboard"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
      </router-link>
      <div class="min-w-0">
        <h1 class="text-sm sm:text-base font-bold text-[#0B0F19] truncate">
          {{ documentTitle || "Naskah Tanpa Judul" }}
        </h1>
        <div class="flex flex-wrap items-center gap-1.5 mt-1">
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border" :class="severity.cls">
            Skor: {{ (scoreComposite ?? 0).toFixed(1) }}% ({{ severity.label }})
          </span>
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border" :class="quotaBadge.cls">
            {{ quotaBadge.label }}
          </span>
        </div>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <div class="hidden xl:flex items-center space-x-1.5 text-xs text-gray-500">
        <span class="px-2 py-1 bg-red-50 text-red-700 rounded-lg border border-red-200 font-medium">
          Leksikal (50%): {{ (scoreLexical ?? 0).toFixed(1) }}%
        </span>
        <span class="px-2 py-1 bg-orange-50 text-orange-700 rounded-lg border border-orange-200 font-medium">
          Semantik (35%): {{ (scoreSemantic ?? 0).toFixed(1) }}%
        </span>
        <span class="px-2 py-1 bg-yellow-50 text-yellow-800 rounded-lg border border-yellow-200 font-medium">
          Stilometri (15%): {{ (scoreStylometric ?? 0).toFixed(1) }}%
        </span>
      </div>

      <button
        type="button"
        @click="handleDownloadPdf"
        :disabled="isExporting"
        class="inline-flex items-center px-3.5 py-2 text-xs font-semibold text-white rounded-xl shadow-sm transition-all"
        :class="isFreeUser ? 'bg-amber-600 hover:bg-amber-700' : 'bg-[#1560BD] hover:bg-[#1A73D9] disabled:opacity-50'"
      >
        <span v-if="isExporting">Menyiapkan PDF...</span>
        <span v-else-if="isFreeUser">Unduh PDF Resmi (Upgrade Premium)</span>
        <span v-else>Unduh Laporan PDF Resmi</span>
      </button>
    </div>
  </header>
</template>
