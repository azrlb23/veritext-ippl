<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { UploadDropzone } from "../components/dashboard";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";
import { documentService } from "../services/documentService";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const isUploading = ref(false);

async function handleStartAudit(payload: { file: File; depth: "FULL" | "TIER1_ONLY"; cost: number }) {
  const cost = payload.cost;
  if (authStore.tokenBalance < cost) {
    showNotification(`Saldo token tidak cukup (butuh ${cost}).`, "warning");
    router.push("/billing");
    return;
  }
  isUploading.value = true;
  try {
    await documentService.upload(payload.file, payload.depth);
    showNotification(`Naskah "${payload.file.name}" masuk antrean.`, "success");
    await authStore.fetchProfile();
    router.push("/riwayat");
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Gagal mengunggah.", "error");
  } finally {
    isUploading.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-[1180px] px-4 pb-20 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-10 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Periksa naskah</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Unggah naskah, <span class="vt-accent">kami periksa.</span>
      </h1>
      <p class="mt-4 max-w-[520px] text-[16px] leading-[1.65] text-[#4B4757]">
        Hasilnya berupa laporan per kalimat yang bisa Anda telusuri dan perbaiki langsung.
      </p>
    </div>

    <UploadDropzone :is-uploading="isUploading" :token-balance="authStore.tokenBalance" @start-audit="handleStartAudit" @topup="router.push('/billing')" />
  </div>
</template>
