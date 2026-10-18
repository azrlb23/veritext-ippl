import { ref } from "vue";

export interface FileUploadOptions {
  allowedExtensions?: string[];
  maxSizeBytes?: number;
}

export function useFileUpload(options: FileUploadOptions = {}) {
  const {
    allowedExtensions = [".pdf", ".docx", ".txt"],
    maxSizeBytes = 50 * 1024 * 1024, // 50 MB
  } = options;

  const selectedFile = ref<File | null>(null);
  const isDragging = ref(false);
  const error = ref<string | null>(null);

  function validateFile(file: File): boolean {
    error.value = null;

    if (file.size > maxSizeBytes) {
      const maxMb = (maxSizeBytes / (1024 * 1024)).toFixed(0);
      error.value = `Ukuran berkas melebihi batas maksimal ${maxMb} MB.`;
      return false;
    }

    const lowerName = file.name.toLowerCase();
    const isExtensionAllowed =
      allowedExtensions.length === 0 ||
      allowedExtensions.some((ext) => lowerName.endsWith(ext.toLowerCase()));

    if (!isExtensionAllowed) {
      error.value = `Format berkas "${file.name}" tidak didukung. Gunakan: ${allowedExtensions.join(", ")}`;
      return false;
    }

    return true;
  }

  function handleFileSelect(file: File | null) {
    if (!file) {
      selectedFile.value = null;
      return;
    }
    if (validateFile(file)) {
      selectedFile.value = file;
    } else {
      selectedFile.value = null;
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    isDragging.value = true;
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    isDragging.value = false;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging.value = false;
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }

  function reset() {
    selectedFile.value = null;
    error.value = null;
    isDragging.value = false;
  }

  return {
    selectedFile,
    isDragging,
    error,
    handleFileSelect,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    reset,
  };
}
