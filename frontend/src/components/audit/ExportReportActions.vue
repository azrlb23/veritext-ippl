<script setup lang="ts">
import { ref } from "vue";

interface Props {
  verificationUuid: string;
  pdfPath?: string | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: "exportPdf"): void;
}>();

const copied = ref(false);

function copyVerifyUrl() {
  const url = `${window.location.origin}/verify/${props.verificationUuid}`;
  navigator.clipboard.writeText(url).then(() => {
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  });
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2.5">
    <!-- Pratinjau QR Publik Pill Button -->
    <router-link
      :to="`/verify/${verificationUuid}`"
      class="px-4 py-2 border border-[#ededed] hover:border-[#17191c] rounded-full text-xs font-medium text-[#17191c] transition-colors bg-white hover:bg-[#fafafb] shadow-sm flex items-center space-x-1.5 active:scale-[0.98]"
    >
      <svg class="w-3.5 h-3.5 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
      <span>Pratinjau QR Publik</span>
    </router-link>

    <!-- Salin Link QR Pill Button -->
    <button
      type="button"
      @click="copyVerifyUrl"
      class="px-4 py-2 border border-[#ededed] hover:border-[#17191c] rounded-full text-xs font-medium text-[#17191c] transition-colors bg-white hover:bg-[#fafafb] shadow-sm flex items-center space-x-1.5 active:scale-[0.98]"
    >
      <svg class="w-3.5 h-3.5 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      <span>{{ copied ? "Tautan Disalin!" : "Salin Link QR" }}</span>
    </button>

    <!-- Unduh Sertifikat PDF Primary Pill Button -->
    <button
      type="button"
      @click="emit('exportPdf')"
      class="px-5 py-2 bg-[#17191c] hover:bg-[#2e3138] text-white rounded-full text-xs font-medium transition-colors shadow-sm flex items-center space-x-1.5 active:scale-[0.98]"
    >
      <svg class="w-3.5 h-3.5 text-white/90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span>Unduh Sertifikat PDF</span>
    </button>
  </div>
</template>
