<script setup lang="ts">
import { ref } from "vue";
import { VtIcon } from "../common";

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
      class="flex min-h-[220px] flex-col items-center justify-center rounded-[32px] p-8 text-center transition-colors duration-200 sm:min-h-[240px]"
      :class="isDragging ? 'border-2 border-dashed border-[#8A3FE0] bg-[#E7D9F8]' : file ? 'bg-[#F3EEFA]' : 'border-2 border-dashed border-[#8A3FE0]/20 bg-[#F3EEFA]/75'"
      @dragover.prevent="emit('dragover', $event)"
      @dragleave="emit('dragleave', $event)"
      @drop.prevent="emit('drop', $event)"
    >
      <template v-if="!file">
        <VtIcon name="upload" class="h-10 w-10 text-[#6D28D9]" />
        <p class="mt-5 text-[19px] font-semibold tracking-[-0.02em] text-[#14111C]">Tarik dan lepas naskah di sini</p>
        <p class="mt-1.5 text-[14px] text-[#5E5A6B]">PDF, DOCX, atau TXT, maksimal 15 MB</p>
        <button
          type="button"
          class="vt-btn-dark mt-6 inline-flex h-12 cursor-pointer items-center rounded-full px-7 text-[14px] font-semibold"
          @click="pick"
        >
          Pilih berkas
        </button>
      </template>

      <template v-else>
        <VtIcon name="document" class="h-10 w-10 text-[#14111C]" />
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
