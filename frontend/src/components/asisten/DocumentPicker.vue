<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import type { DocumentItem } from "../../types";

const props = defineProps<{ documents: DocumentItem[]; modelValue: string[] }>();
const emit = defineEmits<{ (e: "update:modelValue", v: string[]): void }>();
const MAX = 3;
const open = ref(false);
const pickerRef = ref<HTMLElement | null>(null);

const selectedDocs = computed(() => props.documents.filter((d) => props.modelValue.includes(d.id)));
const triggerLabel = computed(() => (props.modelValue.length > 0 ? `${props.modelValue.length} naskah dipilih` : "Pilih naskah (opsional, maks 3)"));

function toggle(id: string) {
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
  <div>
    <p v-if="documents.length === 0" class="text-[14px] text-[#5E5A6B]">
      Belum ada naskah. Unggah di halaman Periksa naskah agar asisten bisa membacanya.
    </p>
    <div v-else ref="pickerRef" class="relative">
      <button
        type="button"
        :aria-expanded="open"
        aria-haspopup="listbox"
        class="vt-btn-light inline-flex h-11 cursor-pointer items-center justify-between gap-3 rounded-full px-5 text-[14px] font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        @click="open = !open"
      >
        <span>{{ triggerLabel }}</span>
        <svg viewBox="0 0 20 20" class="h-4 w-4 text-[#4B4757] transition-transform duration-150" :class="open ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 7.5L10 12.5L15 7.5" /></svg>
      </button>

      <div
        v-if="open"
        role="listbox"
        aria-multiselectable="true"
        class="mt-2 z-30 max-h-60 w-full max-w-md overflow-y-auto rounded-[20px] border border-[#E8ECEB] bg-white p-2 shadow-float"
      >
        <button
          v-for="d in documents"
          :key="d.id"
          type="button"
          role="option"
          :aria-selected="modelValue.includes(d.id)"
          :disabled="!modelValue.includes(d.id) && modelValue.length >= MAX"
          class="flex min-h-[44px] w-full cursor-pointer items-center gap-3 rounded-xl px-3.5 py-2 text-left text-[14px] text-[#14111C] transition-colors hover:bg-[#F4F5F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-50"
          @click="toggle(d.id)"
        >
          <span
            class="flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors"
            :class="modelValue.includes(d.id) ? 'border-[#0F766E] bg-[#0F766E] text-white' : 'border-[#CBD5E1] bg-white'"
            aria-hidden="true"
          >
            <svg v-if="modelValue.includes(d.id)" viewBox="0 0 16 16" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.5L6.5 11.5L12.5 5" /></svg>
          </span>
          <span class="truncate">{{ d.original_filename }}</span>
        </button>
      </div>

      <div v-if="selectedDocs.length > 0" class="mt-3 flex flex-wrap gap-2">
        <button
          v-for="d in selectedDocs"
          :key="d.id"
          type="button"
          :aria-label="`Batal pilih ${d.original_filename}`"
          class="inline-flex min-h-[44px] max-w-full cursor-pointer items-center gap-2 rounded-full border border-[#D5ECE8] bg-[#EBF8F6] px-4 text-[13px] font-medium text-[#0F766E] transition-colors hover:bg-[#D5ECE8]/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          @click="toggle(d.id)"
        >
          <span class="truncate">{{ d.original_filename }}</span>
          <svg viewBox="0 0 16 16" class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>
