<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from "vue";
import type { ChatHistoryItem } from "../../services/chatService";
import { formatChatBlocks } from "../../utils/formatChat";

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
        v-if="m.role === 'USER'"
        class="max-w-[88%] whitespace-pre-wrap rounded-[24px] bg-[#14111C] px-5 py-3.5 text-[15.5px] leading-[1.6] text-white sm:max-w-[75%]"
      >{{ m.content }}</p>
      <div
        v-else
        class="max-w-[88%] space-y-2 rounded-[24px] border border-[#D5ECE8] bg-[#EBF8F6] px-5 py-3.5 text-[15.5px] leading-[1.6] text-[#14111C] sm:max-w-[75%]"
      >
        <template v-for="(block, bi) in formatChatBlocks(m.content)" :key="bi">
          <h3 v-if="block.type === 'heading'" class="pt-0.5 text-[15.5px] font-semibold text-[#0F766E]">
            <template v-for="(s, si) in block.spans" :key="si">
              <strong v-if="s.bold" class="font-semibold">{{ s.text }}</strong>
              <em v-else-if="s.italic">{{ s.text }}</em>
              <code v-else-if="s.code" class="rounded bg-white/80 px-1.5 py-0.5 font-mono text-[13.5px] text-[#0F766E]">{{ s.text }}</code>
              <template v-else>{{ s.text }}</template>
            </template>
          </h3>
          <div v-else-if="block.type === 'list'" class="flex items-start gap-2 pl-1">
            <span class="shrink-0 font-semibold text-[#0F766E]">{{ block.marker }}</span>
            <p class="min-w-0 flex-1">
              <template v-for="(s, si) in block.spans" :key="si">
                <strong v-if="s.bold" class="font-semibold">{{ s.text }}</strong>
                <em v-else-if="s.italic">{{ s.text }}</em>
                <code v-else-if="s.code" class="rounded bg-white/80 px-1.5 py-0.5 font-mono text-[13.5px] text-[#0F766E]">{{ s.text }}</code>
                <template v-else>{{ s.text }}</template>
              </template>
            </p>
          </div>
          <p v-else class="whitespace-pre-line">
            <template v-for="(s, si) in block.spans" :key="si">
              <strong v-if="s.bold" class="font-semibold">{{ s.text }}</strong>
              <em v-else-if="s.italic">{{ s.text }}</em>
              <code v-else-if="s.code" class="rounded bg-white/80 px-1.5 py-0.5 font-mono text-[13.5px] text-[#0F766E]">{{ s.text }}</code>
              <template v-else>{{ s.text }}</template>
            </template>
          </p>
        </template>
      </div>
      <button
        v-if="m.role === 'ASSISTANT'"
        type="button"
        class="mt-1 inline-flex min-h-[44px] cursor-pointer items-center rounded-full px-3.5 text-[12.5px] font-medium text-[#4B4757] transition-colors hover:bg-[#F4F5F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        :aria-label="copiedId === m.id ? 'Pesan tersalin' : 'Salin jawaban asisten'"
        @click="copyMessage(m.id, m.content)"
      >{{ copiedId === m.id ? "Tersalin" : "Salin" }}</button>
    </div>
    <div v-if="sending" class="flex justify-start">
      <p class="rounded-[24px] border border-[#D5ECE8] bg-[#EBF8F6] px-5 py-3.5 text-[15px] text-[#5E5A6B]">Asisten sedang menulis...</p>
    </div>
  </div>
</template>
