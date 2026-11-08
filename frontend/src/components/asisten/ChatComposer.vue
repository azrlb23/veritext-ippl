<script setup lang="ts">
import { ref } from "vue";

defineProps<{ disabled: boolean; error: string }>();
const emit = defineEmits<{ (e: "send", text: string): void }>();
const text = ref("");

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
  <form class="pt-4" @submit.prevent="submit">
    <p v-if="error" class="mb-3 text-[14px] font-medium text-[#B91C1C]" role="alert">{{ error }}</p>
    <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
      <label class="block flex-1">
        <span class="sr-only">Pesan untuk asisten</span>
        <textarea
          v-model="text"
          rows="2"
          maxlength="4000"
          placeholder="Tulis pertanyaan tentang naskah Anda"
          class="block min-h-[56px] w-full resize-none border-0 border-b-2 border-[#14111C]/20 bg-transparent py-2 text-[16px] text-[#14111C] outline-none transition-colors placeholder:text-[#6B6679] focus:border-[#8A3FE0]"
          @keydown="onKey"
        ></textarea>
      </label>
      <button
        type="submit"
        :disabled="disabled || !text.trim()"
        class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >Kirim</button>
    </div>
  </form>
</template>
