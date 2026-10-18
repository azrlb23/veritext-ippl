<script setup lang="ts">
import { ref } from "vue";
import Button from "../common/Button.vue";

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
    <router-link
      :to="`/verify/${verificationUuid}`"
      class="px-3.5 py-1.5 border border-[#ededed] hover:border-[#d4d4d4] rounded-[4px] text-xs font-medium text-[#262626] transition-colors shadow-none bg-white hover:bg-[#fafafa] flex items-center space-x-1.5"
    >
      <span>🔍</span>
      <span>Pratinjau QR Publik</span>
    </router-link>

    <Button
      variant="outline"
      size="sm"
      @click="copyVerifyUrl"
    >
      <template #prefix>
        <span>🔗</span>
      </template>
      {{ copied ? "Tautan Disalin!" : "Salin Link QR" }}
    </Button>

    <Button
      variant="primary"
      size="sm"
      @click="emit('exportPdf')"
    >
      <template #prefix>
        <span>📥</span>
      </template>
      Unduh Sertifikat PDF
    </Button>
  </div>
</template>
