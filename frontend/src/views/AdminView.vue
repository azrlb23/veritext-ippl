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
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8 font-sans">
    <!-- Header with overview anchor -->
    <div id="overview" class="scroll-mt-28 bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-6 sm:p-7 shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <span class="text-[11px] font-bold text-[#1560BD] bg-[#EAF3FE] border border-[#BFDBFE] px-3 py-1 rounded-full uppercase tracking-wider">
          Panel Pemantauan Sistem - Read-Only
        </span>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0B0F19] tracking-tight mt-2.5">Panel Pemantauan Sistem</h1>
        <p class="text-xs sm:text-sm text-[#5B6475] mt-1">Observabilitas metrik global, transaksi Midtrans, dan log audit</p>
      </div>
      <button
        type="button"
        :disabled="isLoading"
        @click="fetchData"
        class="inline-flex items-center justify-center px-5 py-2.5 rounded-full border border-[#E4E8F0] bg-white text-xs font-semibold text-[#0B0F19] hover:bg-slate-50 active:scale-[0.98] transition-colors transition-transform duration-150 shadow-xs cursor-pointer disabled:opacity-50"
      >
        <span v-if="isLoading">Memuat Data...</span>
        <span v-else>Muat Ulang Data</span>
      </button>
    </div>

    <!-- Error State with Retry Button -->
    <div v-if="hasError && !isLoading" class="bg-rose-50/90 border border-rose-200 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
      <div>
        <h3 class="text-xs sm:text-sm font-bold text-rose-800">Gagal Mengambil Data Pemantauan</h3>
        <p class="text-xs text-rose-600 mt-0.5">{{ errorMessage || "Terjadi kendala jaringan saat menyinkronkan data pemantauan." }}</p>
      </div>
      <button
        type="button"
        @click="fetchData"
        class="px-4 py-2 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-xs active:scale-[0.98] transition-colors transition-transform duration-150 cursor-pointer self-start sm:self-auto"
      >
        Coba Lagi
      </button>
    </div>

    <!-- KPI Analytics Cards -->
    <GlobalAnalyticsCards :data="analytics" :loading="isLoading" />

    <!-- Infrastructure Telemetry -->
    <div id="health" class="scroll-mt-28">
      <SystemHealthPanel :health="health" :loading="isLoading" />
    </div>

    <!-- Transactions and Audit Logs -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start">
      <div id="transactions" class="scroll-mt-28 h-full">
        <TransactionLogTable :transactions="transactions" :loading="isLoading" />
      </div>
      <div id="logs" class="scroll-mt-28 h-full">
        <AuditLogTable
          :logs="auditLogs"
          :loading="isLoading"
          :page="logPage"
          :pages="logPages"
          :total="logTotal"
          :selectedAction="selectedAction"
          @update:selectedAction="handleActionFilter"
          @changePage="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>
