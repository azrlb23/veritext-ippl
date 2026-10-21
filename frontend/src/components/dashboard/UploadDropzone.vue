<script setup lang="ts">
import { ref } from "vue";
import { useFileUpload } from "../../composables";
import Alert from "../common/Alert.vue";

interface Props {
  isUploading?: boolean;
}

withDefaults(defineProps<Props>(), {
  isUploading: false,
});

const emit = defineEmits<{
  (e: "startAudit", payload: { file: File; depth: "FULL" | "TIER1_ONLY" }): void;
}>();

const auditDepth = ref<"FULL" | "TIER1_ONLY">("FULL");

const {
  selectedFile,
  isDragging,
  error: uploadError,
  handleFileSelect,
  handleDragOver,
  handleDragLeave,
  handleDrop,
  reset,
} = useFileUpload({
  allowedExtensions: [".pdf", ".docx", ".txt"],
  maxSizeBytes: 50 * 1024 * 1024,
});

const fileInputRef = ref<HTMLInputElement | null>(null);

function handleFileReset() {
  reset();
  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
}

function onFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0]);
  }
}

function handleStart() {
  if (!selectedFile.value) return;
  const fileToUpload = selectedFile.value;
  const depth = auditDepth.value;
  handleFileReset();
  emit("startAudit", {
    file: fileToUpload,
    depth,
  });
}

function triggerFilePicker() {
  fileInputRef.value?.click();
}

defineExpose({
  reset: handleFileReset,
  triggerFilePicker,
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[22px] p-6 sm:p-7 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] space-y-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-[#17191c]"></span>
        <h2 class="text-xs font-semibold uppercase tracking-wider text-[#17191c]">
          Unggah Berkas Naskah <span class="italic font-normal text-[#777b86]">(.pdf, .docx, .txt)</span>
        </h2>
      </div>
      <span class="text-xs text-[#777b86] font-normal">Maks. 50 MB / berkas</span>
    </div>

    <!-- Alert on error -->
    <Alert
      v-if="uploadError"
      variant="error"
      title="Format Berkas Tidak Sesuai"
      :message="uploadError"
      dismissible
      @dismiss="uploadError = null"
    />

    <!-- Dropzone -->
    <div
      class="border border-dashed rounded-[20px] p-8 text-center transition-all duration-150 ease-out cursor-pointer"
      :class="[
        isDragging ? 'border-[#17191c] bg-[#fafafb] scale-[1.005]' : 'border-[#ededed] hover:border-[#17191c] bg-[#fafafb]',
        selectedFile ? 'border-[#17191c] bg-white' : '',
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <input
        ref="fileInputRef"
        type="file"
        id="dashboardDocUpload"
        accept=".pdf,.docx,.txt"
        @change="onFileInputChange"
        class="hidden"
      />
      <label for="dashboardDocUpload" class="cursor-pointer space-y-2 block">
        <div class="mx-auto w-12 h-12 rounded-full bg-white border border-[#ededed] text-[#17191c] flex items-center justify-center shadow-sm">
          <svg v-if="selectedFile" class="w-6 h-6 text-[#17191c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <svg v-else class="w-6 h-6 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>

        <div v-if="selectedFile" class="space-y-1">
          <div class="text-sm font-semibold text-[#17191c]">
            {{ selectedFile.name }}
          </div>
          <div class="text-xs text-[#777b86] font-normal">
            Ukuran: {{ (selectedFile.size / 1024).toFixed(1) }} KB
          </div>
          <button
            type="button"
            @click.stop.prevent="handleFileReset"
            class="text-xs text-red-600 hover:underline pt-1 font-medium"
          >
            Ganti berkas
          </button>
        </div>

        <div v-else class="space-y-1">
          <div class="text-sm font-medium text-[#17191c]">
            Klik untuk memilih berkas atau seret naskah ke sini
          </div>
          <p class="text-xs text-[#777b86] font-normal">
            Format yang didukung: Dokumen Teks <strong class="italic font-medium text-[#17191c]">PDF</strong>, Microsoft Word <strong class="italic font-medium text-[#17191c]">DOCX</strong>, atau Plain Text <strong class="italic font-medium text-[#17191c]">TXT</strong>
          </p>
        </div>
      </label>
    </div>

    <!-- Depth selector & Action -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-[#ededed]">
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-xs font-medium text-[#777b86]">Tingkat Kedalaman:</span>
        <label
          class="inline-flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-full border cursor-pointer transition-colors"
          :class="auditDepth === 'FULL' ? 'bg-[#17191c] text-white border-[#17191c]' : 'bg-[#fafafb] text-[#17191c] border-[#ededed]'"
        >
          <input
            type="radio"
            value="FULL"
            v-model="auditDepth"
            class="hidden"
          />
          <span>Hybrid Penuh (Tier 1-4) &bull; 2 Token</span>
        </label>
        <label
          class="inline-flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-full border cursor-pointer transition-colors"
          :class="auditDepth === 'TIER1_ONLY' ? 'bg-[#17191c] text-white border-[#17191c]' : 'bg-[#fafafb] text-[#17191c] border-[#ededed]'"
        >
          <input
            type="radio"
            value="TIER1_ONLY"
            v-model="auditDepth"
            class="hidden"
          />
          <span>Leksikal Saja (Tier 1) &bull; 1 Token</span>
        </label>
      </div>

      <button
        type="button"
        :disabled="!selectedFile || isUploading"
        @click="handleStart"
        class="inline-flex items-center justify-center px-6 py-2.5 rounded-full bg-[#17191c] hover:bg-[#2e3138] disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-xs tracking-tight active:scale-[0.98] transition-all duration-150 ease-out shadow-sm"
      >
        <span v-if="isUploading">Memproses Unggahan...</span>
        <span v-else>Mulai Proses Audit &rarr;</span>
      </button>
    </div>
  </div>
</template>
