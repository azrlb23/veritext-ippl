<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{ disabled: boolean; error: string; modelValue?: string }>();
const emit = defineEmits<{ (e: "send", text: string): void; (e: "update:modelValue", v: string): void }>();

const localText = ref("");
const text = computed({
  get: () => props.modelValue ?? localText.value,
  set: (v: string) => { localText.value = v; emit("update:modelValue", v); },
});

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
    <p v-if="error" class="mb-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>
    <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
      <label class="block flex-1">
        <span class="sr-only">Pesan untuk asisten</span>
        <textarea
          v-model="text"
          rows="2"
          maxlength="4000"
          placeholder="Tulis pertanyaan naskah atau tempel kalimat untuk diparafrase"
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
