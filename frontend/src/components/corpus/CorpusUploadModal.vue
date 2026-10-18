<script setup lang="ts">
import { ref } from "vue";
import Modal from "../common/Modal.vue";
import Button from "../common/Button.vue";
import Alert from "../common/Alert.vue";
import { useFileUpload } from "../../composables";

interface Props {
  isOpen: boolean;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "close"): void;
  (e: "submit", payload: { title: string; category: string; academicYear: string; file?: File | null }): void;
}>();

const archiveName = ref("");
const category = ref("Informatika");
const academicYear = ref("2025/2026");
const errorMessage = ref("");
const fileInputRef = ref<HTMLInputElement | null>(null);

const {
  selectedFile,
  isDragging,
  error: fileError,
  handleFileSelect,
  handleDragOver,
  handleDragLeave,
  handleDrop,
  reset: resetFile,
} = useFileUpload({
  allowedExtensions: [".zip", ".tar.gz", ".tar"],
  maxSizeBytes: 100 * 1024 * 1024,
});

function onFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    handleFileSelect(file);
    if (!archiveName.value) {
      archiveName.value = file.name;
    }
  }
}

function handleResetFile() {
  resetFile();
  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
}

function handleSubmit() {
  const finalTitle = archiveName.value.trim() || selectedFile.value?.name;
  if (!finalTitle && !selectedFile.value) {
    errorMessage.value = "Silakan pilih berkas arsip ZIP atau isi nama koleksi korpus.";
    return;
  }
  errorMessage.value = "";
  emit("submit", {
    title: finalTitle || "Arsip_Korpus.zip",
    category: category.value,
    academicYear: academicYear.value,
    file: selectedFile.value,
  });
  archiveName.value = "";
  handleResetFile();
}
</script>

<template>
  <Modal
    :isOpen="isOpen"
    title="Unggah Arsip Korpus (ZIP)"
    maxWidth="md"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <p class="text-xs text-audyr-ash leading-relaxed">
        Unggah berkas arsip naskah (.zip) untuk diindeksasi otomatis ke dalam database <span class="italic font-bold text-audyr-ink">pgvector (HNSW)</span> dan tabel sidik jari leksikal.
      </p>

      <Alert
        v-if="errorMessage || fileError"
        variant="error"
        :message="errorMessage || fileError || ''"
        dismissible
        @dismiss="errorMessage = ''"
      />

      <!-- File Dropzone -->
      <div
        class="border border-dashed rounded-[8px] p-5 text-center transition-all cursor-pointer"
        :class="[
          isDragging ? 'border-audyr-ink bg-[#fafafa]' : 'border-[#ededed] hover:border-audyr-ink bg-white',
          selectedFile ? 'border-audyr-ink bg-white' : '',
        ]"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <input
          ref="fileInputRef"
          type="file"
          id="corpusZipUpload"
          accept=".zip,.tar.gz,.tar"
          @change="onFileInputChange"
          class="hidden"
        />
        <label for="corpusZipUpload" class="cursor-pointer space-y-1 block">
          <div class="text-2xl">📦</div>
          <div v-if="selectedFile">
            <span class="text-xs font-bold text-audyr-ink block">{{ selectedFile.name }}</span>
            <span class="text-[11px] text-audyr-ash tabular-nums font-bold">{{ (selectedFile.size / (1024 * 1024)).toFixed(2) }} MB</span>
            <div>
              <button
                type="button"
                @click.stop.prevent="handleResetFile"
                class="text-[11px] text-red-600 hover:underline pt-0.5 tracking-tight font-medium"
              >
                Ganti berkas
              </button>
            </div>
          </div>
          <div v-else class="text-xs text-audyr-ash">
            <span class="font-bold text-audyr-ink">Klik untuk memilih</span> atau seret file arsip .ZIP (Maks 100 MB)
          </div>
        </label>
      </div>

      <div class="space-y-1">
        <label class="block text-xs font-bold text-audyr-ink tracking-tight">Nama Koleksi / Judul Korpus</label>
        <input
          v-model="archiveName"
          type="text"
          placeholder="Jurnal_Fasilkom_2026.zip"
          class="w-full px-3.5 py-2 rounded-[4px] border border-[#ededed] text-xs text-audyr-ink placeholder:text-audyr-fog focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1">
          <label class="block text-xs font-semibold text-audyr-ink tracking-tight">Kategori Bidang</label>
          <select
            v-model="category"
            class="w-full px-3 py-2 rounded-[4px] border border-[#ededed] text-xs text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
          >
            <option value="Informatika">Informatika</option>
            <option value="Sistem Informasi">Sistem Informasi</option>
            <option value="Ilmu Komputer">Ilmu Komputer</option>
            <option value="Teknik Elektro">Teknik Elektro</option>
            <option value="Umum">Umum</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-semibold text-audyr-ink tracking-tight">Tahun Akademik</label>
          <input
            v-model="academicYear"
            type="text"
            placeholder="2025/2026"
            class="w-full px-3 py-2 rounded-[4px] border border-[#ededed] text-xs text-audyr-ink placeholder:text-audyr-fog focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        variant="ghost"
        size="sm"
        @click="emit('close')"
      >
        Batal
      </Button>
      <Button
        variant="primary"
        size="sm"
        :loading="loading"
        @click="handleSubmit"
      >
        Mulai Ingest & Indeksasi &rarr;
      </Button>
    </template>
  </Modal>
</template>
