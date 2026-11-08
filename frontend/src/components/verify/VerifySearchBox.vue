<script setup lang="ts">
import { ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    initialValue?: string;
    loading?: boolean;
  }>(),
  { initialValue: "", loading: false }
);

const emit = defineEmits<{
  (e: "verify", uuid: string): void;
}>();

const inputUuid = ref(props.initialValue);
watch(() => props.initialValue, (val) => { inputUuid.value = val; });

function handleVerify() {
  if (inputUuid.value.trim() && !props.loading) {
    emit("verify", inputUuid.value.trim());
  }
}
</script>

<template>
  <div class="space-y-3 font-sans">
    <div
      class="bg-white rounded-full p-2 pl-5 sm:pl-6 border border-[#E4E8F0] shadow-[0_10px_30px_rgba(138,152,184,0.12)] flex flex-col sm:flex-row items-center gap-2.5 transition-colors focus-within:border-[#1560BD]"
    >
      <div class="relative flex-grow w-full flex items-center">
        <svg class="w-4 h-4 text-[#8E98AB] flex-shrink-0 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="inputUuid"
          type="text"
          placeholder="Masukkan UUID Sertifikat (contoh: 8f2a91c4-b7e1-4d90-a35c-7e6189df0123)"
          class="w-full py-2.5 pr-3 text-sm font-medium text-[#0B0F19] placeholder:text-[#8E98AB] bg-transparent border-0 focus:outline-none tracking-tight font-sans"
          @keyup.enter="handleVerify"
        />
        <button
          v-if="inputUuid"
          type="button"
          @click="inputUuid = ''"
          class="text-[#8E98AB] hover:text-[#0B0F19] text-xs p-1 mr-1 transition-colors cursor-pointer"
          title="Bersihkan input"
        >
          &times;
        </button>
      </div>

      <button
        type="button"
        :disabled="!inputUuid.trim() || loading"
        @click="handleVerify"
        class="w-full sm:w-auto inline-flex items-center justify-center px-7 py-3 rounded-full bg-[#0B0F19] hover:bg-[#1E2330] disabled:bg-[#DCE3F0] disabled:text-[#8E98AB] disabled:cursor-not-allowed text-white font-semibold text-xs sm:text-[13px] tracking-tight active:scale-[0.98] transition-colors transition-transform duration-150 shadow-xs whitespace-nowrap cursor-pointer font-sans"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span v-if="loading">Memvalidasi...</span>
        <span v-else class="flex items-center gap-1.5">
          <span>Verifikasi Sertifikat</span>
          <span class="font-bold">&rarr;</span>
        </span>
      </button>
    </div>

    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs text-[#5B6475] px-2 gap-2">
      <span>Format UUID 36-karakter tertera pada footer sertifikat audit naskah VeriText AI.</span>
      <span class="text-[#1560BD] font-medium">Pindai QR pada sertifikat dengan kamera ponsel; tautan akan membuka halaman ini otomatis.</span>
    </div>
  </div>
</template>
