<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import ChatComposer from "../components/asisten/ChatComposer.vue";
import MessageList from "../components/asisten/MessageList.vue";
import PriorityFixModal from "../components/asisten/PriorityFixModal.vue";
import QuickActions from "../components/asisten/QuickActions.vue";
import SessionList from "../components/asisten/SessionList.vue";
import { useAssistant } from "../composables/useAssistant";
import { auditService } from "../services/auditService";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const authStore = useAuthStore();
const a = useAssistant();
const showList = ref(false);
const priorityOpen = ref(false);
const downloading = ref<"docx" | "pdf" | null>(null);

onMounted(() => {
  const doc = route.query.doc;
  if (typeof doc === "string" && doc && !a.selectedDocs.value.includes(doc) && a.selectedDocs.value.length < 3) {
    a.selectedDocs.value = [...a.selectedDocs.value, doc];
  }
  const sentence = route.query.sentence;
  if (typeof sentence === "string" && sentence) {
    a.focusSentenceId.value = sentence;
  }
});

async function open(id: string | null) {
  await a.openSession(id);
  showList.value = false;
}

async function downloadDoc(format: "docx" | "pdf") {
  const reportId = a.linkedAudit.value?.reportId;
  if (!reportId) return;
  downloading.value = format;
  try {
    await auditService.downloadRevisedDocument(reportId, format);
  } catch {
    a.error.value = "Gagal mengunduh naskah revisi. Silakan coba lagi.";
  } finally {
    downloading.value = null;
  }
}
</script>

<template>
  <div class="mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7">
    <div class="mb-6 max-w-4xl">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Teman menulis yang membaca naskah Anda.
      </h1>
    </div>

    <section class="grid overflow-hidden rounded-[36px] border border-[#E8ECEB] bg-white shadow-float lg:grid-cols-[310px_1fr]" aria-label="Asisten AI">
      <aside class="bg-[#F4F8F7] border-r border-[#E6ECEB] p-4 lg:p-5">
        <button
          type="button"
          class="vt-btn-light mb-3 inline-flex h-11 w-full cursor-pointer items-center justify-between rounded-full px-5 text-[14px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] lg:hidden"
          :aria-expanded="showList"
          @click="showList = !showList"
        >Percakapan ({{ a.sessions.value.length }})<span aria-hidden="true">{{ showList ? "Tutup" : "Buka" }}</span></button>
        <div :class="showList ? 'block' : 'hidden lg:block'" class="max-h-[50vh] lg:max-h-none lg:h-[676px]">
          <SessionList :sessions="a.sessions.value" :active-id="a.activeId.value" @open="open" @remove="a.removeSession" />
        </div>
      </aside>

      <div class="flex min-h-[520px] flex-col p-5 sm:p-8 lg:h-[740px]">
        <div v-if="a.linkedAudit.value" class="mb-4 flex flex-wrap items-center gap-2 border-b border-[#E8ECEB] pb-3">
          <button type="button" class="vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2" @click="priorityOpen = true">Perbaiki 5 kalimat prioritas</button>
          <router-link :to="`/audits/${a.linkedAudit.value.taskId}`" class="inline-flex h-10 items-center rounded-full px-3.5 text-[13px] font-semibold text-[#0F766E] transition-colors hover:bg-[#EBF8F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]">Lihat hasil audit</router-link>
          <template v-if="authStore.role !== 'FREE'">
            <button type="button" :disabled="Boolean(downloading)" class="vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-40" @click="downloadDoc('docx')">{{ downloading === "docx" ? "Menyiapkan..." : "Revisi DOCX" }}</button>
            <button type="button" :disabled="Boolean(downloading)" class="vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-40" @click="downloadDoc('pdf')">{{ downloading === "pdf" ? "Menyiapkan..." : "Revisi PDF" }}</button>
          </template>
        </div>

        <template v-if="a.messages.value.length === 0 && !a.sending.value">
          <div class="flex-1 overflow-y-auto no-scrollbar">
            <h2 class="text-[24px] font-semibold tracking-[-0.03em] text-[#14111C]">Apa yang ingin Anda perbaiki?</h2>
            <p class="mt-2 max-w-lg text-[15px] leading-relaxed text-[#4B4757]">
              Tanyakan isi naskah, minta saran perbaikan gaya penulisan, atau tempel kalimat untuk diparafrase.
            </p>
            <QuickActions
              :doc-count="a.selectedDocs.value.length"
              :has-focus-sentence="Boolean(a.focusSentenceId.value)"
              @pick="({ prompt, taskMode }) => a.send(prompt, taskMode)"
            />
          </div>
        </template>
        <MessageList v-else :messages="a.messages.value" :sending="a.sending.value" />

        <div
          v-if="a.focusSentenceId.value"
          class="mt-2 flex items-center justify-between gap-3 border-l-2 border-[#0F766E] pl-3 text-[13px] text-[#0F766E]"
        >
          <span class="truncate font-medium">Fokus pada kalimat audit terpilih</span>
          <button
            type="button"
            class="inline-flex min-h-[44px] shrink-0 cursor-pointer items-center px-2 font-semibold underline underline-offset-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            @click="a.focusSentenceId.value = null"
          >Lepas</button>
        </div>
        <p v-if="a.trialLeft.value !== null && authStore.role === 'FREE'" class="mt-3 text-[13px] text-[#5E5A6B]">Sisa percobaan gratis: {{ a.trialLeft.value }}</p>
        <ChatComposer
          v-model="a.draft.value"
          v-model:selected-docs="a.selectedDocs.value"
          :documents="a.documents.value"
          :can-attach="!a.activeId.value"
          :disabled="a.sending.value"
          :error="a.error.value"
          @send="a.send"
        />
      </div>
    </section>

    <PriorityFixModal
      v-if="a.linkedAudit.value"
      :open="priorityOpen"
      :document-id="a.linkedAudit.value.documentId"
      :is-free="authStore.role === 'FREE'"
      @close="priorityOpen = false"
    />
  </div>
</template>
