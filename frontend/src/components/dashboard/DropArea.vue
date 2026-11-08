<script setup lang="ts">
import { ref } from "vue";

defineProps<{ file: File | null; isDragging: boolean; error: string }>();
const emit = defineEmits<{
  (e: "select", file: File): void;
  (e: "reset"): void;
  (e: "dragover", ev: DragEvent): void;
  (e: "dragleave", ev: DragEvent): void;
  (e: "drop", ev: DragEvent): void;
}>();

const input = ref<HTMLInputElement | null>(null);

function onChange(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) emit("select", target.files[0]);
}

function pick() {
  input.value?.click();
}

function clear() {
  if (input.value) input.value.value = "";
  emit("reset");
}

defineExpose({ clear, pick });
</script>

<template>
  <div>
    <input ref="input" type="file" accept=".pdf,.docx,.txt" class="hidden" aria-label="Pilih berkas naskah" @change="onChange" />

    <div
      class="flex min-h-[300px] flex-col items-center justify-center rounded-[28px] p-8 text-center transition-colors duration-200"
      :class="isDragging ? 'bg-[#E7D9F8]' : 'bg-[#F3EEFA]'"
      @dragover.prevent="emit('dragover', $event)"
      @dragleave="emit('dragleave', $event)"
      @drop.prevent="emit('drop', $event)"
    >
      <template v-if="!file">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-white text-[#6D28D9] shadow-lift">
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 16V4m0 0l-4 4m4-4l4 4M5 16v2a2 2 0 002 2h10a2 2 0 002-2v-2" />
          </svg>
        </div>
        <p class="mt-5 text-[19px] font-semibold tracking-[-0.02em] text-[#14111C]">Tarik dan lepas naskah di sini</p>
        <p class="mt-1.5 text-[14px] text-[#5E5A6B]">PDF, DOCX, atau TXT, maksimal 15 MB</p>
        <button
          type="button"
          class="mt-6 inline-flex h-12 cursor-pointer items-center rounded-full bg-[#14111C] px-7 text-[14px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
          @click="pick"
        >
          Pilih berkas
        </button>
      </template>

      <template v-else>
        <div class="flex h-16 w-16 items-center justify-center rounded-[20px] bg-white text-[#14111C] shadow-lift">
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6" />
          </svg>
        </div>
        <p class="mt-5 max-w-full truncate text-[19px] font-semibold tracking-[-0.02em] text-[#14111C]">{{ file.name }}</p>
        <p class="mt-1.5 text-[14px] tabular-nums text-[#5E5A6B]">{{ (file.size / (1024 * 1024)).toFixed(2) }} MB</p>
        <div class="mt-6 flex flex-wrap items-center justify-center gap-3">
          <button
            type="button"
            class="inline-flex h-11 cursor-pointer items-center rounded-full bg-white px-6 text-[14px] font-semibold text-[#14111C] shadow-lift transition-transform duration-200 hover:-translate-y-0.5"
            @click="pick"
          >
            Ganti naskah
          </button>
          <button type="button" class="inline-flex h-11 cursor-pointer items-center rounded-full px-4 text-[14px] font-medium text-[#5E5A6B] transition-colors hover:text-[#B91C1C]" @click="clear">
            Hapus
          </button>
        </div>
      </template>
    </div>

    <p v-if="error" role="alert" class="mt-3 text-[14px] font-medium text-[#B91C1C]">{{ error }}</p>
  </div>
</template>
