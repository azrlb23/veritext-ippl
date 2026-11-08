import { ref } from "vue";
import { documentService, type DocumentEstimate } from "../services/documentService";

export function useUploadEstimate() {
  const estimate = ref<DocumentEstimate | null>(null);
  const isEstimating = ref(false);
  const estimateError = ref("");
  let requestId = 0;

  async function run(file: File) {
    const current = ++requestId;
    isEstimating.value = true;
    estimateError.value = "";
    estimate.value = null;
    try {
      const result = await documentService.estimate(file);
      if (current === requestId) estimate.value = result;
    } catch (err: any) {
      if (current === requestId) {
        estimateError.value = err?.response?.data?.detail || "Jumlah kata belum bisa dihitung. Coba pilih berkas lagi.";
      }
    } finally {
      if (current === requestId) isEstimating.value = false;
    }
  }

  function clear() {
    requestId++;
    estimate.value = null;
    estimateError.value = "";
    isEstimating.value = false;
  }

  return { estimate, isEstimating, estimateError, run, clear };
}
