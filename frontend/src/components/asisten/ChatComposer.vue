<script setup lang="ts">
import { computed, ref } from "vue";
import type { DocumentItem } from "../../types";
import DocumentPicker from "./DocumentPicker.vue";

const props = withDefaults(
  defineProps<{
    disabled: boolean;
    error: string;
    modelValue?: string;
    documents?: DocumentItem[];
    selectedDocs?: string[];
    canAttach?: boolean;
  }>(),
  { documents: () => [], selectedDocs: () => [], canAttach: true }
);
const emit = defineEmits<{
  (e: "send", text: string): void;
  (e: "update:modelValue", v: string): void;
  (e: "update:selectedDocs", v: string[]): void;
}>();

const localText = ref("");
const text = computed({
  get: () => props.modelValue ?? localText.value,
  set: (v: string) => { localText.value = v; emit("update:modelValue", v); },
});
const attached = computed(() => props.documents.filter((d) => props.selectedDocs.includes(d.id)));

function removeDoc(id: string) {
  if (!props.canAttach) return;
  emit("update:selectedDocs", props.selectedDocs.filter((x) => x !== id));
}

function submit() {
  const value = text.value.trim();
  if (props.disabled || !value) return;
  emit("send", value);
  text.value = "";
}

function onKey(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submit();
  }
}
</script>

<template>
  <form class="border-t border-[#E8ECEB] pt-3" @submit.prevent="submit">
    <p v-if="error" class="mb-2.5 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>

    <div v-if="attached.length > 0" class="mb-2.5 flex flex-wrap gap-1.5">
      <button
        v-for="d in attached"
        :key="d.id"
        type="button"
        :disabled="!canAttach"
        class="inline-flex h-7 max-w-full cursor-pointer items-center gap-1.5 rounded-full bg-[#EBF8F6] px-3 text-[12px] font-medium text-[#0F766E] transition-colors hover:bg-[#D5ECE8] disabled:cursor-default disabled:hover:bg-[#EBF8F6]"
        @click="removeDoc(d.id)"
      >
        <span class="truncate">{{ d.original_filename }}</span>
        <svg v-if="canAttach" viewBox="0 0 16 16" class="h-3 w-3 shrink-0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8" /></svg>
      </button>
    </div>

    <div class="flex items-end gap-2.5">
      <DocumentPicker
        :documents="documents"
        :model-value="selectedDocs"
        :disabled="!canAttach"
        @update:model-value="emit('update:selectedDocs', $event)"
      />
      <label class="block flex-1">
        <span class="sr-only">Pesan untuk asisten</span>
        <textarea
          v-model="text"
          rows="2"
          maxlength="4000"
          placeholder="Tulis pertanyaan naskah atau tempel kalimat untuk diparafrase"
          class="block min-h-[48px] w-full resize-none border-0 border-b-2 border-[#14111C]/20 bg-transparent py-2 text-[15.5px] text-[#14111C] outline-none transition-colors placeholder:text-[#5E5A6B] focus:border-[#0F766E]"
          @keydown="onKey"
        ></textarea>
      </label>
      <button
        type="submit"
        :disabled="disabled || !text.trim()"
        class="vt-btn-dark inline-flex h-11 shrink-0 cursor-pointer items-center justify-center rounded-full px-7 text-[14.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40"
      >Kirim</button>
    </div>
  </form>
</template>
