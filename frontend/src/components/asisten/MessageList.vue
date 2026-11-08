<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import type { ChatHistoryItem } from "../../services/chatService";

const props = defineProps<{ messages: ChatHistoryItem[]; sending: boolean }>();
const box = ref<HTMLElement | null>(null);
watch(() => [props.messages.length, props.sending], () => nextTick(() => box.value?.scrollTo({ top: box.value.scrollHeight, behavior: "smooth" })));
</script>

<template>
  <div ref="box" class="flex-1 space-y-4 overflow-y-auto px-1 py-2" aria-live="polite">
    <div v-for="m in messages" :key="m.id" class="flex" :class="m.role === 'USER' ? 'justify-end' : 'justify-start'">
      <p
        class="max-w-[88%] whitespace-pre-wrap rounded-[24px] px-5 py-3.5 text-[15.5px] leading-[1.6] sm:max-w-[75%]"
        :class="m.role === 'USER' ? 'bg-[#14111C] text-white' : 'bg-[#F3EEFA] text-[#14111C]'"
      >{{ m.content }}</p>
    </div>
    <div v-if="sending" class="flex justify-start">
      <p class="rounded-[24px] bg-[#F3EEFA] px-5 py-3.5 text-[15px] text-[#5E5A6B]">Asisten sedang menulis...</p>
    </div>
  </div>
</template>
