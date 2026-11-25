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
      v-if="!file"
      class="flex min-h-[200px] flex-col items-center justify-center rounded-2xl border border-dashed px-6 py-10 text-center transition-colors duration-200"
      :class="isDragging ? 'border-[#0F766E] bg-[#D5ECE8]/45' : 'border-[#0F766E]/30 bg-white/35 hover:border-[#0F766E]/50'"
      @dragover.prevent="emit('dragover', $event)"
      @dragleave="emit('dragleave', $event)"
      @drop.prevent="emit('drop', $event)"
    >
      <VtIcon name="upload" tone="current" class="h-8 w-8 text-[#0F766E]" />
      <p class="mt-4 text-[17px] font-semibold tracking-[-0.02em] text-[#14111C]">Tarik dan lepas naskah di sini</p>
      <p class="mt-1 text-[13.5px] text-[#5E5A6B]">PDF, DOCX, atau TXT, maksimal 15 MB</p>
      <button
        type="button"
        class="vt-btn-dark mt-5 inline-flex h-11 cursor-pointer items-center rounded-full px-6 text-[13.5px] font-semibold"
        @click="pick"
      >
        Pilih berkas
      </button>
    </div>

    <div
      v-else
      class="flex flex-col gap-4 border-y border-[#E6ECEB] py-5 transition-colors duration-200 sm:flex-row sm:items-center sm:justify-between"
      :class="isDragging ? 'border-[#0F766E] bg-[#EBF8F6]/50 px-3' : ''"
      @dragover.prevent="emit('dragover', $event)"
      @dragleave="emit('dragleave', $event)"
      @drop.prevent="emit('drop', $event)"
    >
      <div class="flex min-w-0 items-center gap-3.5">
        <VtIcon name="document" tone="current" class="h-7 w-7 shrink-0 text-[#0F766E]" />
        <div class="min-w-0">
          <p class="truncate text-[16.5px] font-semibold tracking-[-0.015em] text-[#14111C]">{{ file.name }}</p>
          <p class="mt-0.5 text-[13px] tabular-nums text-[#5E5A6B]">
            {{ (file.size / (1024 * 1024)).toFixed(2) }} MB · Siap diperiksa
          </p>
        </div>
      </div>

      <div class="flex shrink-0 items-center gap-2">
        <button
          type="button"
          class="vt-btn-light inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold"
          @click="pick"
        >
          Ganti naskah
        </button>
        <button
          type="button"
          class="inline-flex h-9 cursor-pointer items-center rounded-full px-3 text-[13px] font-medium text-[#5E5A6B] transition-colors hover:text-[#B91C1C]"
          @click="clear"
        >
          Hapus
        </button>
      </div>
    </div>

    <p v-if="error" role="alert" class="mt-3 text-[13.5px] font-medium text-[#B91C1C]">{{ error }}</p>
  </div>
</template>
