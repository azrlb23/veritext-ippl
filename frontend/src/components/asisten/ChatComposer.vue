<script setup lang="ts">
import { computed, ref } from "vue";

const props = withDefaults(
  defineProps<{
    disabled: boolean;
    error: string;
    taskMode?: string;
    preferredEngine?: string;
    lastEngine?: string;
  }>(),
  { taskMode: "QA_DOCUMENT", preferredEngine: "auto", lastEngine: "" }
);

const emit = defineEmits<{
  (e: "send", text: string): void;
  (e: "update:taskMode", val: string): void;
  (e: "update:preferredEngine", val: string): void;
}>();

const text = ref("");

const placeholderText = computed(() => {
  if (props.taskMode === "PARAPHRASE_TASK") return "Tempel kalimat atau paragraf yang ingin diparafrasekan...";
  if (props.taskMode === "STYLE_REVIEW") return "Tempel paragraf untuk ditinjau gaya bahasa dan pola AI-nya...";
  return "Tulis pertanyaan tentang isi naskah Anda...";
});

function submit() {
  const value = text.value.trim();
  if (!value) return;
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
  <form class="pt-3" @submit.prevent="submit">
    <p v-if="error" class="mb-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>
    <div class="mb-2 flex flex-wrap items-center gap-2 border-t border-[#E8ECEB] pt-3">
      <div class="flex items-center gap-1.5">
        <label for="composer-task-mode" class="text-[12.5px] font-medium text-[#4B4757]">Tugas</label>
        <select
          id="composer-task-mode"
          :value="taskMode"
          class="h-11 cursor-pointer rounded-full border border-[#E8ECEB] bg-[#F8FAF9] px-4 text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          @change="emit('update:taskMode', ($event.target as HTMLSelectElement).value)"
        >
          <option value="QA_DOCUMENT">Tanya isi naskah</option>
          <option value="PARAPHRASE_TASK">Parafrase teks</option>
          <option value="STYLE_REVIEW">Tinjau gaya &amp; pola AI</option>
        </select>
      </div>
      <div class="flex items-center gap-1.5">
        <label for="composer-preferred-engine" class="text-[12.5px] font-medium text-[#4B4757]">Mesin AI</label>
        <select
          id="composer-preferred-engine"
          :value="preferredEngine"
          class="h-11 cursor-pointer rounded-full border border-[#E8ECEB] bg-[#F8FAF9] px-4 text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          @change="emit('update:preferredEngine', ($event.target as HTMLSelectElement).value)"
        >
          <option value="auto">Otomatis (Cloud -&gt; Lokal)</option>
          <option value="ollama">Ollama Lokal (qwen2.5:7b)</option>
          <option value="gemini">Gemini Flash (Cloud)</option>
        </select>
      </div>
      <span v-if="lastEngine" class="ml-auto text-[12.5px] font-medium text-[#0F766E]">Aktif: {{ lastEngine }}</span>
    </div>
    <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
      <label class="block flex-1">
        <span class="sr-only">Pesan untuk asisten</span>
        <textarea
          v-model="text"
          rows="2"
          maxlength="4000"
          :placeholder="placeholderText"
          class="block min-h-[56px] w-full resize-none border-0 border-b-2 border-[#14111C]/20 bg-transparent py-2 text-[16px] text-[#14111C] outline-none transition-colors placeholder:text-[#5E5A6B] focus:border-[#0F766E]"
          @keydown="onKey"
        ></textarea>
      </label>
      <button
        type="submit"
        :disabled="disabled || !text.trim()"
        class="vt-btn-dark inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >Kirim</button>
    </div>
  </form>
</template>
