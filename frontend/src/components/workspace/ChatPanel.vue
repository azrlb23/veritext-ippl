<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import type { HeatmapAnnotation } from "../../types";
import ChatComposer from "../asisten/ChatComposer.vue";
import MessageList from "../asisten/MessageList.vue";
import { chatService, type ChatHistoryItem } from "../../services/chatService";
import { friendlyChatError } from "../../composables/useAssistant";
import { useAuthStore } from "../../stores/auth";

const authStore = useAuthStore();

const props = defineProps<{ documentId: string; selected?: HeatmapAnnotation | null }>();
const messages = ref<ChatHistoryItem[]>([]);
const sessionId = ref("");
const sending = ref(false);
const error = ref("");
const panelRef = ref<HTMLElement | null>(null);

const SUGGESTED_PROMPTS = [
  "Jelaskan bagian yang paling mirip",
  "Bagaimana cara mengutip bagian ini (APA)?",
  "Ringkas bagian yang perlu direvisi",
];

watch(
  () => [messages.value.length, sending.value],
  () => {
    void nextTick(() => {
      const box = panelRef.value?.querySelector("[aria-live='polite']");
      if (box) box.scrollTo({ top: box.scrollHeight, behavior: "smooth" });
    });
  },
);

async function send(prompt: string) {
  if (sending.value) return;
  error.value = "";
  sending.value = true;
  messages.value.push({ id: `u-${Date.now()}`, role: "USER", content: prompt, created_at: "" });
  try {
    const res = await chatService.sendMessage(prompt, {
      documentIds: sessionId.value ? [] : [props.documentId],
      sessionId: sessionId.value || undefined,
      sentenceId: props.selected?.sentence_id,
    });
    sessionId.value = res.session_id;
    messages.value.push({ id: res.message_id, role: "ASSISTANT", content: res.content, created_at: "" });
    void authStore.fetchProfile();
  } catch (err: any) {
    messages.value.pop();
    error.value = friendlyChatError(err);
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <div ref="panelRef" class="flex h-[480px] flex-col">
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-[#E8ECEB] pb-3 text-[13px]">
      <span class="font-medium text-[#4B4757]">Membaca naskah</span>
      <span v-if="selected" class="rounded-full bg-[#F4F5F6] px-3 py-1 text-[12px] font-medium text-[#14111C]">Fokus: kalimat terpilih</span>
    </div>

    <div v-if="messages.length === 0 && !sending" class="flex flex-1 flex-col justify-between py-1">
      <p class="text-[15px] leading-relaxed text-[#4B4757]">Tanyakan apa saja tentang hasil ini, termasuk cara merevisi kalimat atau merapikan sitasi.</p>
      <div class="mt-4 flex flex-col gap-2">
        <button
          v-for="prompt in SUGGESTED_PROMPTS"
          :key="prompt"
          type="button"
          class="vt-btn-light inline-flex min-h-[42px] cursor-pointer items-center justify-start rounded-full px-4 py-2 text-left text-[13.5px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          @click="send(prompt)"
        >{{ prompt }}</button>
      </div>
    </div>
    <MessageList v-else :messages="messages" :sending="sending" />
    <ChatComposer :disabled="sending" :error="error" @send="send" />
  </div>
</template>
