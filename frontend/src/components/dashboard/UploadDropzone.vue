<script setup lang="ts">
import { ref } from "vue";
import { useFileUpload } from "../../composables";
import Button from "../common/Button.vue";
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

defineExpose({
  reset: handleFileReset,
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-extrabold uppercase tracking-wider text-[#262626]">
        1. Unggah Berkas Naskah <span class="italic font-bold text-[#686868]">(.pdf, .docx, .txt)</span>
      </h2>
      <span class="text-xs text-[#737373] font-medium">Maks. 50 MB / berkas</span>
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
      class="border border-dashed rounded-[14px] p-8 text-center transition-colors duration-150 ease-out cursor-pointer"
      :class="[
        isDragging ? 'border-[#262626] bg-[#fafafa] scale-[1.005]' : 'border-[#ededed] hover:border-[#cbcbcb] bg-[#fafafa]',
        selectedFile ? 'border-[#262626] bg-white' : '',
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
        <div class="mx-auto w-12 h-12 rounded-[8px] bg-white border border-[#ededed] text-[#262626] flex items-center justify-center text-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
          {{ selectedFile ? '📑' : '📤' }}
        </div>

        <div v-if="selectedFile" class="space-y-1">
          <div class="text-sm font-extrabold text-[#262626]">
            {{ selectedFile.name }}
          </div>
          <div class="text-xs text-[#737373] font-medium">
            Ukuran: {{ (selectedFile.size / 1024).toFixed(1) }} KB
          </div>
          <button
            type="button"
            @click.stop.prevent="handleFileReset"
            class="text-xs text-red-600 hover:underline pt-1 font-bold"
          >
            Ganti berkas
          </button>
        </div>

        <div v-else class="space-y-1">
          <div class="text-sm font-bold text-[#262626]">
            Klik untuk memilih berkas atau seret naskah ke sini
          </div>
          <p class="text-xs text-[#737373] font-normal">
            Format yang didukung: Dokumen Teks <strong class="italic font-bold text-[#515151]">PDF</strong>, Microsoft Word <strong class="italic font-bold text-[#515151]">DOCX</strong>, atau Plain Text <strong class="italic font-bold text-[#515151]">TXT</strong>
          </p>
        </div>
      </label>
    </div>

    <!-- Depth selector & Action -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-[#ededed]">
      <div class="flex flex-wrap items-center gap-4">
        <span class="text-xs font-semibold text-[#737373]">Pilihan Tingkat Kedalaman:</span>
        <label class="inline-flex items-center space-x-2 text-xs font-semibold text-[#262626] cursor-pointer">
          <input
            type="radio"
            value="FULL"
            v-model="auditDepth"
            class="text-[#262626] focus:ring-[#262626]"
          />
          <span>Penuh (Tier 1 - 4) &bull; <strong class="italic font-bold text-[#262626]">2 Token</strong></span>
        </label>
        <label class="inline-flex items-center space-x-2 text-xs font-semibold text-[#262626] cursor-pointer">
          <input
            type="radio"
            value="TIER1_ONLY"
            v-model="auditDepth"
            class="text-[#262626] focus:ring-[#262626]"
          />
          <span>Hanya Leksikal (Tier 1) &bull; <strong class="italic font-bold text-[#262626]">1 Token</strong></span>
        </label>
      </div>

      <Button
        variant="primary"
        size="md"
        :loading="isUploading"
        :disabled="!selectedFile || isUploading"
        @click="handleStart"
      >
        <template #prefix>
          <span>🚀</span>
        </template>
        {{ isUploading ? "Memproses Unggahan..." : "Mulai Proses Audit →" }}
      </Button>
    </div>
  </div>
</template>
