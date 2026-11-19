<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { UploadDropzone } from "../components/dashboard";
import { useAuthStore } from "../stores/auth";
import { useNotification, useSectionReveal } from "../composables";
import { documentService } from "../services/documentService";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
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
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1180px] px-4 pb-16 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-5 max-w-4xl">
      <p class="text-[13px] font-medium text-[#5E5A6B]">Periksa naskah</p>
      <h1 class="mt-1.5 text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Unggah naskah, <span class="vt-accent">kami periksa.</span>
      </h1>
      <p class="mt-1.5 max-w-[540px] text-[14.5px] leading-[1.6] text-[#4B4757]">
        Hasilnya berupa laporan per kalimat yang bisa Anda telusuri dan perbaiki langsung.
      </p>
    </div>

    <div class="vt-reveal vt-d-1">
      <UploadDropzone :is-uploading="isUploading" :token-balance="authStore.tokenBalance" @start-audit="handleStartAudit" @topup="router.push('/billing')" />
    </div>
  </div>
</template>
