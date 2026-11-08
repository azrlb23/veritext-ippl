<script setup lang="ts">
import { ref } from "vue";
import type { HeatmapAnnotation } from "../../types";
import ChatComposer from "../asisten/ChatComposer.vue";
import MessageList from "../asisten/MessageList.vue";
import { chatService, type ChatHistoryItem } from "../../services/chatService";
import { friendlyChatError } from "../../composables/useAssistant";

const props = defineProps<{ documentId: string; selected?: HeatmapAnnotation | null }>();
const messages = ref<ChatHistoryItem[]>([]);
const sessionId = ref("");
const sending = ref(false);
const error = ref("");

async function send(prompt: string) {
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
  } catch (err: any) {
    messages.value.pop();
    error.value = friendlyChatError(err);
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <div class="flex h-[460px] flex-col">
    <p v-if="messages.length === 0 && !sending" class="flex-1 text-[15px] leading-relaxed text-[#4B4757]">Tanyakan apa saja tentang hasil ini, misalnya cara memperbaiki bagian yang paling mirip. Asisten ikut membaca naskah ini.</p>
    <MessageList v-else :messages="messages" :sending="sending" />
    <ChatComposer :disabled="sending" :error="error" @send="send" />
  </div>
</template>
