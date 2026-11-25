<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import type { DocumentItem } from "../../types";

const props = withDefaults(defineProps<{ documents: DocumentItem[]; modelValue: string[]; disabled?: boolean }>(), {
  disabled: false,
});
const emit = defineEmits<{ (e: "update:modelValue", v: string[]): void }>();
const MAX = 3;
const open = ref(false);
const pickerRef = ref<HTMLElement | null>(null);

const count = computed(() => props.modelValue.length);
const titleText = computed(() =>
  props.disabled
    ? "Mulai percakapan baru untuk mengubah lampiran naskah"
    : count.value > 0
      ? `${count.value} naskah terlampir (maks ${MAX})`
      : "Lampirkan laporan/naskah (maks 3)"
);

function toggle(id: string) {
  if (props.disabled) return;
  if (props.modelValue.includes(id)) return emit("update:modelValue", props.modelValue.filter((x) => x !== id));
  if (props.modelValue.length < MAX) emit("update:modelValue", [...props.modelValue, id]);
}
function onDocClick(e: MouseEvent) {
  if (open.value && pickerRef.value && !pickerRef.value.contains(e.target as Node)) open.value = false;
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape" && open.value) open.value = false;
}
onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onKeydown);
});
onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div ref="pickerRef" class="relative shrink-0">
    <button
      type="button"
      :disabled="disabled || documents.length === 0"
      :aria-expanded="open"
      aria-haspopup="listbox"
      :title="documents.length === 0 ? 'Belum ada naskah diunggah' : titleText"
      :aria-label="titleText"
      class="relative inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-full border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-40"
      :class="count > 0 ? 'border-[#0F766E]/40 bg-[#EBF8F6] text-[#0F766E]' : 'border-[#E6ECEB] bg-white text-[#5E5A6B] hover:border-[#CBD5E1] hover:text-[#14111C]'"
      @click="open = !open"
    >
      <!-- Simbol lampiran paperclip -->
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
      </svg>
      <span
        v-if="count > 0"
        class="absolute -right-1 -top-1 flex h-4.5 min-w-[18px] items-center justify-center rounded-full bg-[#0F766E] px-1 text-[10px] font-bold text-white"
      >{{ count }}</span>
    </button>

    <div
      v-if="open && !disabled"
      role="listbox"
      aria-multiselectable="true"
      class="absolute bottom-full left-0 z-30 mb-2 max-h-64 w-72 overflow-y-auto rounded-[20px] border border-[#E8ECEB] bg-white p-2 shadow-float sm:w-80"
    >
      <div class="px-3 py-1.5 text-[12px] font-semibold text-[#5E5A6B]">Lampirkan laporan naskah (maks 3)</div>
      <button
        v-for="d in documents"
        :key="d.id"
        type="button"
        role="option"
        :aria-selected="modelValue.includes(d.id)"
        :disabled="!modelValue.includes(d.id) && modelValue.length >= MAX"
        class="flex min-h-[42px] w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-left text-[13.5px] text-[#14111C] transition-colors hover:bg-[#F4F5F6] focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        @click="toggle(d.id)"
      >
        <span
          class="flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded border transition-colors"
          :class="modelValue.includes(d.id) ? 'border-[#0F766E] bg-[#0F766E] text-white' : 'border-[#CBD5E1] bg-white'"
          aria-hidden="true"
        >
          <svg v-if="modelValue.includes(d.id)" viewBox="0 0 16 16" class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.5L6.5 11.5L12.5 5" /></svg>
        </span>
        <span class="truncate">{{ d.original_filename }}</span>
      </button>
    </div>
  </div>
</template>
