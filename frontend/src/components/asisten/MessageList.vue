<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from "vue";
import type { ChatHistoryItem } from "../../services/chatService";

const props = defineProps<{ messages: ChatHistoryItem[]; sending: boolean }>();
const box = ref<HTMLElement | null>(null);
const copiedId = ref<string | null>(null);
let timer: ReturnType<typeof setTimeout> | null = null;

async function copyMessage(id: string, content: string) {
  try {
    await navigator.clipboard.writeText(content);
    copiedId.value = id;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => { copiedId.value = null; }, 1500);
  } catch {
    copiedId.value = null;
  }
}

watch(() => [props.messages.length, props.sending], () => nextTick(() => box.value?.scrollTo({ top: box.value.scrollHeight, behavior: "smooth" })));
onUnmounted(() => { if (timer) clearTimeout(timer); });
</script>

<template>
  <div ref="box" class="flex-1 space-y-4 overflow-y-auto no-scrollbar px-1 py-2" aria-live="polite">
    <div v-for="m in messages" :key="m.id" class="flex flex-col" :class="m.role === 'USER' ? 'items-end' : 'items-start'">
      <p
        class="max-w-[88%] whitespace-pre-wrap rounded-[24px] px-5 py-3.5 text-[15.5px] leading-[1.6] sm:max-w-[75%]"
        :class="m.role === 'USER' ? 'bg-[#14111C] text-white' : 'border border-[#D5ECE8] bg-[#EBF8F6] text-[#14111C]'"
      >{{ m.content }}</p>
      <button
        v-if="m.role === 'ASSISTANT'"
        type="button"
        class="mt-1 inline-flex h-9 cursor-pointer items-center rounded-full px-3.5 text-[12.5px] font-medium text-[#4B4757] transition-colors hover:bg-[#F4F5F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        :aria-label="copiedId === m.id ? 'Pesan tersalin' : 'Salin jawaban asisten'"
        @click="copyMessage(m.id, m.content)"
      >{{ copiedId === m.id ? "Tersalin" : "Salin" }}</button>
    </div>
    <div v-if="sending" class="flex justify-start">
      <p class="rounded-[24px] border border-[#D5ECE8] bg-[#EBF8F6] px-5 py-3.5 text-[15px] text-[#5E5A6B]">Asisten sedang menulis...</p>
    </div>
  </div>
</template>
