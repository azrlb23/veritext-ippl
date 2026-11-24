<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useAdminData, useSectionReveal } from "../composables";
import { AuditLogTable } from "../components/admin";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { loading, error, logs, logsMeta, fetchLogs } = useAdminData();

const selectedAction = ref("");
const selectedResult = ref<"" | "FAILED">("");
const page = ref(1);

function loadLogs() {
  void fetchLogs({ action_type: selectedAction.value, result: selectedResult.value, page: page.value });
}

function handleAction(action: string) {
  selectedAction.value = action;
  page.value = 1;
  loadLogs();
}

function handleResult(result: "" | "FAILED") {
  selectedResult.value = result;
  page.value = 1;
  loadLogs();
}

function handlePage(nextPage: number) {
  page.value = nextPage;
  loadLogs();
}

onMounted(loadLogs);
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Catatan aktivitas dan keamanan.
      </h1>
      <button type="button" :disabled="loading" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-50" @click="loadLogs">
        {{ loading ? "Memuat..." : "Muat ulang" }}
      </button>
    </div>

    <div v-if="error && !loading" class="vt-reveal mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ error }}</p>
      <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold" @click="loadLogs">Coba lagi</button>
    </div>

    <div class="vt-reveal vt-d-1">
      <AuditLogTable
        :logs="logs"
        :loading="loading"
        :page="logsMeta.page"
        :pages="logsMeta.pages"
        :total="logsMeta.total"
        :selected-action="selectedAction"
        :selected-result="selectedResult"
        @update:selected-action="handleAction"
        @update:selected-result="handleResult"
        @change-page="handlePage"
      />
    </div>
  </div>
</template>
