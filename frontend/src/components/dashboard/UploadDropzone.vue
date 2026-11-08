<script setup lang="ts">
import { ref, computed } from "vue";
import { useFileUpload } from "../../composables";

interface Props {
  isUploading?: boolean;
  tokenBalance?: number;
}
const props = withDefaults(defineProps<Props>(), { isUploading: false, tokenBalance: 3 });

const emit = defineEmits<{
  (e: "startAudit", payload: { file: File; depth: "FULL" | "TIER1_ONLY" }): void;
  (e: "topup"): void;
}>();

const auditDepth = ref<"FULL" | "TIER1_ONLY">("FULL");
const consentChecked = ref(true);
const fileInputRef = ref<HTMLInputElement | null>(null);

const { selectedFile, isDragging, error: uploadError, handleFileSelect, handleDragOver, handleDragLeave, handleDrop, reset } = useFileUpload({
  allowedExtensions: [".pdf", ".docx", ".txt"],
  maxSizeBytes: 50 * 1024 * 1024,
});

const tokenCost = computed(() => (auditDepth.value === "FULL" ? 2 : 1));
const isTokenInsufficient = computed(() => props.tokenBalance < tokenCost.value);
const isConsentValid = computed(() => auditDepth.value !== "FULL" || consentChecked.value);
const isReady = computed(() => Boolean(selectedFile.value) && !isTokenInsufficient.value && !props.isUploading && isConsentValid.value);

function handleFileReset() {
  reset();
  if (fileInputRef.value) fileInputRef.value.value = "";
}

function onFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) handleFileSelect(target.files[0]);
}

function handleStart() {
  if (!isReady.value || !selectedFile.value) return;
  emit("startAudit", { file: selectedFile.value, depth: auditDepth.value });
}

function triggerFilePicker() { fileInputRef.value?.click(); }
defineExpose({ reset: handleFileReset, triggerFilePicker });
</script>

<template>
  <div class="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-5 font-sans select-none">
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Unggah Naskah</h2>
        <p class="text-xs text-slate-500">Ekstraksi teks otomatis dari PDF, DOCX, dan TXT</p>
      </div>
      <span class="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-600 hidden sm:inline">Maksimal 50 MB (PDF, DOCX, TXT)</span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
      <div class="lg:col-span-7 flex flex-col justify-between">
        <input ref="fileInputRef" type="file" accept=".pdf,.docx,.txt" class="hidden" @change="onFileInputChange" />
        <div
          class="relative h-full min-h-[200px] rounded-2xl transition-all flex flex-col items-center justify-center p-5 text-center"
          :class="[isDragging ? 'bg-blue-50 border-2 border-dashed border-blue-600' : selectedFile ? 'bg-slate-50 border border-slate-200' : 'bg-slate-50 border-2 border-dashed border-slate-300 hover:border-blue-500']"
          @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop"
        >
          <div v-if="!selectedFile" class="space-y-2">
            <div class="w-12 h-12 rounded-full bg-white flex items-center justify-center text-blue-600 mx-auto shadow-xs border border-slate-200">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
            </div>
            <p class="text-sm font-bold text-slate-900">Tarik &amp; lepas naskah di sini</p>
            <p class="text-xs text-slate-500">Format .pdf, .docx, .txt (maks. 50 MB)</p>
            <button type="button" @click="triggerFilePicker" class="px-4 py-1.5 rounded-full text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 cursor-pointer">Pilih Berkas &rarr;</button>
          </div>
          <div v-else class="w-full flex flex-col justify-between h-full space-y-3 text-left">
            <div class="flex items-start justify-between">
              <div>
                <div class="text-sm font-bold text-slate-900 truncate max-w-[280px]">{{ selectedFile.name }}</div>
                <div class="text-xs text-slate-500">{{ (selectedFile.size / (1024 * 1024)).toFixed(2) }} MB</div>
              </div>
              <button type="button" @click="handleFileReset" class="text-slate-400 hover:text-red-600 p-1 cursor-pointer">&times;</button>
            </div>
            <button type="button" @click="triggerFilePicker" class="text-xs font-semibold text-blue-600 hover:underline">Ganti naskah</button>
          </div>
        </div>
        <p v-if="uploadError" class="text-xs text-red-600 font-semibold mt-2">{{ uploadError }}</p>
      </div>

      <div class="lg:col-span-5 flex flex-col justify-between space-y-4 bg-slate-50 rounded-2xl p-5 border border-slate-200">
        <div class="space-y-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Kedalaman Scan Audit</div>
          <div @click="auditDepth = 'FULL'" class="flex items-center justify-between p-3 rounded-xl cursor-pointer border text-xs" :class="[auditDepth === 'FULL' ? 'bg-white border-blue-600 font-bold shadow-xs' : 'bg-white/60 border-slate-200 text-slate-600']">
            <div>
              <span class="block text-slate-900">Audit Penuh Hibrida</span>
              <span class="text-[11px] text-slate-500 font-normal">Leksikal, Semantik &amp; AI Evaluator</span>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-200">2 token</span>
          </div>
          <div @click="auditDepth = 'TIER1_ONLY'" class="flex items-center justify-between p-3 rounded-xl cursor-pointer border text-xs" :class="[auditDepth === 'TIER1_ONLY' ? 'bg-white border-blue-600 font-bold shadow-xs' : 'bg-white/60 border-slate-200 text-slate-600']">
            <div>
              <span class="block text-slate-900">Pindai Cepat</span>
              <span class="text-[11px] text-slate-500 font-normal">Leksikal &amp; Stilometri Dasar</span>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200">1 token</span>
          </div>
          <label v-if="auditDepth === 'FULL'" class="flex items-start gap-2 cursor-pointer text-[11px] text-slate-600 pt-1">
            <input type="checkbox" v-model="consentChecked" class="mt-0.5 rounded text-blue-600" />
            <span>Setujui pemrosesan teks naskah untuk evaluasi integritas AI.</span>
          </label>
          <div v-if="isTokenInsufficient" class="text-xs text-red-600 font-semibold bg-red-50 p-2.5 rounded-xl border border-red-200">
            Saldo token tidak cukup (sisa {{ tokenBalance }}). <button type="button" @click="emit('topup')" class="text-blue-600 underline font-bold">Top up kuota</button>
          </div>
        </div>
        <button type="button" :disabled="!isReady" @click="handleStart" class="w-full py-2.5 rounded-full text-xs font-semibold transition-all cursor-pointer" :class="[isReady ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm' : 'bg-slate-200 text-slate-400 cursor-not-allowed']">
          {{ isUploading ? 'Mengunggah ke Antrean...' : 'Mulai Proses Audit Naskah &rarr;' }}
        </button>
      </div>
    </div>
  </div>
</template>
