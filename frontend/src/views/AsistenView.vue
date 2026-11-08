<script setup lang="ts">
import { ref } from "vue";
import ChatComposer from "../components/asisten/ChatComposer.vue";
import DocumentPicker from "../components/asisten/DocumentPicker.vue";
import MessageList from "../components/asisten/MessageList.vue";
import SessionList from "../components/asisten/SessionList.vue";
import { useAssistant } from "../composables/useAssistant";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const a = useAssistant();
const showList = ref(false);

async function open(id: string | null) {
  await a.openSession(id);
  showList.value = false;
}
</script>

<template>
  <div class="mx-auto max-w-[1180px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-9 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Asisten AI</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Teman menulis yang <span class="vt-accent">membaca naskah Anda.</span>
      </h1>
    </div>

    <section class="grid overflow-hidden rounded-[36px] bg-white shadow-float lg:grid-cols-[300px_1fr]" aria-label="Asisten AI">
      <aside class="bg-[#F3EEFA] p-4 lg:p-5">
        <button
          type="button"
          class="mb-3 inline-flex h-11 w-full cursor-pointer items-center justify-between rounded-full bg-white px-5 text-[14px] font-semibold text-[#14111C] shadow-lift lg:hidden"
          :aria-expanded="showList"
          @click="showList = !showList"
        >Percakapan ({{ a.sessions.value.length }})<span aria-hidden="true">{{ showList ? "Tutup" : "Buka" }}</span></button>
        <div :class="showList ? 'block' : 'hidden lg:block'" class="max-h-[50vh] lg:max-h-none lg:h-[640px]">
          <SessionList :sessions="a.sessions.value" :active-id="a.activeId.value" @open="open" @remove="a.removeSession" />
        </div>
      </aside>

      <div class="flex min-h-[520px] flex-col p-5 sm:p-8 lg:h-[704px]">
        <template v-if="a.messages.value.length === 0 && !a.sending.value">
          <div class="flex-1">
            <h2 class="text-[24px] font-semibold tracking-[-0.03em] text-[#14111C]">Apa yang ingin Anda perbaiki?</h2>
            <p class="mt-2 max-w-lg text-[15px] leading-relaxed text-[#4B4757]">
              Minta saran gaya, struktur, atau cara menulis ulang bagian yang mirip. Asisten membaca kutipan paling relevan dari naskah yang Anda pilih.
            </p>
            <div v-if="!a.activeId.value" class="mt-7"><DocumentPicker v-model="a.selectedDocs.value" :documents="a.documents.value" /></div>
          </div>
        </template>
        <MessageList v-else :messages="a.messages.value" :sending="a.sending.value" />

        <p v-if="a.trialLeft.value !== null && authStore.role === 'FREE'" class="mt-3 text-[13px] text-[#5E5A6B]">Sisa percobaan gratis: {{ a.trialLeft.value }}</p>
        <ChatComposer :disabled="a.sending.value" :error="a.error.value" @send="a.send" />
      </div>
    </section>
  </div>
</template>
