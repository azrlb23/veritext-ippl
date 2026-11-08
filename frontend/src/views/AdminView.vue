<script setup lang="ts">
import { ref, onMounted } from "vue";
import { apiClient } from "../services/api";
import { useNotification } from "../composables";
import { GlobalAnalyticsCards, SystemHealthPanel, TransactionLogTable, AuditLogTable } from "../components/admin";

const { showNotification } = useNotification();
const isLoading = ref(false);
const hasError = ref(false);
const errorMessage = ref("");

const analytics = ref({ total_documents: 0, avg_similarity: 0, total_revenue: 0, active_users: 0 });
const transactions = ref([]);
const health = ref({
  database_status: "HEALTHY",
  db_latency_ms: 0,
  total_vector_chunks: 0,
  redis_status: "HEALTHY",
  celery_active_tasks: 0,
  total_audits: 0,
  total_corpus_docs: 0,
});
const auditLogs = ref([]);
const logPage = ref(1);
const logPages = ref(1);
const logTotal = ref(0);
const selectedAction = ref("");

async function fetchData() {
  isLoading.value = true;
  hasError.value = false;
  errorMessage.value = "";
  try {
    const [resAnalytics, resHealth, resTx, resLogs] = await Promise.all([
      apiClient.get("/admin/analytics"),
      apiClient.get("/admin/system-health"),
      apiClient.get("/admin/transactions", { params: { limit: 20 } }),
      apiClient.get("/admin/audit-logs", {
        params: { page: logPage.value, limit: 10, action_type: selectedAction.value || undefined },
      }),
    ]);
    if (resAnalytics.data?.data) analytics.value = resAnalytics.data.data;
    if (resHealth.data?.data) health.value = resHealth.data.data;
    if (resTx.data?.data?.items) transactions.value = resTx.data.data.items;
    if (resLogs.data?.data) {
      auditLogs.value = resLogs.data.data.items || [];
      logPages.value = resLogs.data.data.pages || 1;
      logTotal.value = resLogs.data.data.total || 0;
    }
  } catch (err: any) {
    hasError.value = true;
    errorMessage.value = err?.response?.data?.detail || "Gagal memuat data monitoring sistem.";
    showNotification(errorMessage.value, "error");
  } finally {
    isLoading.value = false;
  }
}

function handlePageChange(p: number) {
  logPage.value = p;
  void fetchData();
}

function handleActionFilter(a: string) {
  selectedAction.value = a;
  logPage.value = 1;
  void fetchData();
}

onMounted(() => {
  void fetchData();
});
</script>

<template>
  <div class="mx-auto max-w-[1180px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div id="overview" class="mb-9 flex scroll-mt-28 flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <div class="max-w-2xl">
        <p class="text-[14px] font-medium text-[#5E5A6B]">Pemantauan</p>
        <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
          Kondisi sistem, <span class="vt-accent">hanya dibaca.</span>
        </h1>
      </div>
      <button type="button" :disabled="isLoading" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-white px-8 text-[15px] font-semibold text-[#14111C] shadow-lift transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] disabled:opacity-50" @click="fetchData">{{ isLoading ? "Memuat..." : "Muat ulang" }}</button>
    </div>

    <div v-if="hasError && !isLoading" class="mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ errorMessage || "Data pemantauan belum bisa dimuat." }}</p>
      <button type="button" class="inline-flex h-11 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[14px] font-semibold text-white shadow-btn-dark" @click="fetchData">Coba lagi</button>
    </div>

    <div class="space-y-6">
      <GlobalAnalyticsCards :data="analytics" :loading="isLoading" />
      <div id="health" class="scroll-mt-28"><SystemHealthPanel :health="health" :loading="isLoading" /></div>
      <div class="grid items-start gap-6 xl:grid-cols-2">
        <div id="transactions" class="h-full scroll-mt-28"><TransactionLogTable :transactions="transactions" :loading="isLoading" /></div>
        <div id="logs" class="h-full scroll-mt-28">
          <AuditLogTable :logs="auditLogs" :loading="isLoading" :page="logPage" :pages="logPages" :total="logTotal" :selectedAction="selectedAction" @update:selectedAction="handleActionFilter" @changePage="handlePageChange" />
        </div>
      </div>
    </div>
  </div>
</template>
