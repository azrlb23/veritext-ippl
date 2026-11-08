<script setup lang="ts">
import { ref, watch } from "vue";

const props = withDefaults(defineProps<{ initialValue?: string; loading?: boolean }>(), { initialValue: "", loading: false });
const emit = defineEmits<{ (e: "verify", uuid: string): void }>();

const inputUuid = ref(props.initialValue);
watch(() => props.initialValue, (val) => { inputUuid.value = val; });

function handleVerify() {
  if (inputUuid.value.trim() && !props.loading) emit("verify", inputUuid.value.trim());
}
</script>

<template>
  <div class="mx-auto max-w-[760px] font-sans">
    <div class="flex flex-col items-stretch gap-2 rounded-[32px] bg-white p-2 pl-6 shadow-float transition-shadow duration-200 focus-within:ring-4 focus-within:ring-[#8A3FE0]/15 sm:flex-row sm:items-center sm:rounded-full">
      <div class="flex min-w-0 flex-grow items-center">
        <svg class="mr-3 h-[18px] w-[18px] shrink-0 text-[#5E5A6B]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="inputUuid"
          type="text"
          aria-label="Kode UUID sertifikat"
          placeholder="Tempel kode UUID sertifikat"
          class="w-full min-w-0 border-0 bg-transparent py-3 pr-3 text-[15px] font-medium tracking-tight text-[#14111C] placeholder:text-[#5E5A6B] focus:outline-none"
          @keyup.enter="handleVerify"
        />
        <button
          v-if="inputUuid"
          type="button"
          aria-label="Bersihkan input"
          @click="inputUuid = ''"
          class="mr-2 cursor-pointer p-1 text-[18px] leading-none text-[#5E5A6B] transition-colors hover:text-[#14111C]"
        >
          &times;
        </button>
      </div>

      <button
        type="button"
        :disabled="!inputUuid.trim() || loading"
        @click="handleVerify"
        class="inline-flex h-[52px] cursor-pointer items-center justify-center whitespace-nowrap rounded-full bg-[#14111C] px-8 text-[14px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-[#D9D3E4] disabled:text-[#5E5A6B] disabled:shadow-none disabled:hover:translate-y-0"
      >
        {{ loading ? "Memvalidasi..." : "Verifikasi sertifikat" }}
      </button>
    </div>

    <p class="mt-4 text-center text-[13px] leading-[1.6] text-[#5E5A6B]">
      Kode UUID ada di bagian bawah sertifikat. Memindai QR akan membuka halaman ini dengan kode terisi.
    </p>

  </div>
</template>
