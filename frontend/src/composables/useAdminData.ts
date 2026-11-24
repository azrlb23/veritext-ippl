import { ref } from "vue";
import { apiClient } from "../services/api";
import { useNotification } from "./useNotification";
import type {
  AdminAnalytics,
  AdminPaginationMeta,
  AdminTransactionItem,
  AdminUserItem,
  AuditLogItem,
  InvoiceSummary,
  OverviewExtras,
  SystemExtras,
  SystemHealthMetrics,
} from "../types/admin";

const emptyMeta = (): AdminPaginationMeta => ({ total: 0, page: 1, limit: 15, pages: 1 });

export function useAdminData() {
  const { showNotification } = useNotification();
  const loading = ref(false);
  const error = ref("");

  const analytics = ref<AdminAnalytics>({ total_documents: 0, avg_similarity: 0, total_revenue: 0, active_users: 0 });
  const overviewExtras = ref<OverviewExtras>({ new_users_7d: 0, audits_today: 0, tokens_spent_30d: 0, role_distribution: { FREE: 0, PREMIUM: 0, ADMIN: 0 }, trends: [] });
  const health = ref<SystemHealthMetrics>({ database_status: "HEALTHY", db_latency_ms: 0, total_vector_chunks: 0, redis_status: "HEALTHY", celery_active_tasks: 0, total_audits: 0, total_corpus_docs: 0 });
  const systemExtras = ref<SystemExtras>({ failed_audits_24h: 0, queued_audits: 0, processing_audits: 0 });

  const users = ref<AdminUserItem[]>([]);
  const usersMeta = ref<AdminPaginationMeta>(emptyMeta());
  const invoices = ref<AdminTransactionItem[]>([]);
  const invoiceSummary = ref<InvoiceSummary>({ total_revenue: 0, paid: 0, pending: 0, failed: 0, top_package: null });
  const invoicesMeta = ref<AdminPaginationMeta>(emptyMeta());
  const logs = ref<AuditLogItem[]>([]);
  const logsMeta = ref<AdminPaginationMeta>(emptyMeta());

  async function runFetch(fallback: string, task: () => Promise<void>) {
    loading.value = true;
    error.value = "";
    try {
      await task();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail;
      const msg = detail || (err as { message?: string })?.message || fallback;
      error.value = msg;
      showNotification(msg, "error");
    } finally {
      loading.value = false;
    }
  }

  async function fetchOverview() {
    await runFetch("Gagal memuat ringkasan monitoring admin.", async () => {
      const [resAnalytics, resOverview, resHealth] = await Promise.all([
        apiClient.get("/admin/analytics"),
        apiClient.get("/admin/overview"),
        apiClient.get("/admin/system-health"),
      ]);
      if (resAnalytics.data?.data) analytics.value = resAnalytics.data.data;
      if (resOverview.data?.data) overviewExtras.value = resOverview.data.data;
      if (resHealth.data?.data) health.value = resHealth.data.data;
    });
  }

  async function fetchUsers(params: { q?: string; role?: string; page?: number } = {}) {
    await runFetch("Gagal memuat daftar pengguna.", async () => {
      const res = await apiClient.get("/admin/users", {
        params: { q: params.q?.trim() || undefined, role: params.role || undefined, page: params.page ?? 1, limit: 15 },
      });
      const d = res.data?.data;
      if (d) {
        users.value = d.items || [];
        usersMeta.value = { total: d.total || 0, page: d.page || 1, limit: d.limit || 15, pages: d.pages || 1 };
      }
    });
  }

  async function fetchInvoices(params: { status?: string; page?: number } = {}) {
    await runFetch("Gagal memuat data transaksi.", async () => {
      const res = await apiClient.get("/admin/invoices", {
        params: { status: params.status || undefined, page: params.page ?? 1, limit: 15 },
      });
      const d = res.data?.data;
      if (d) {
        invoices.value = d.items || [];
        if (d.summary) invoiceSummary.value = d.summary;
        invoicesMeta.value = { total: d.total || 0, page: d.page || 1, limit: d.limit || 15, pages: d.pages || 1 };
      }
    });
  }

  async function fetchLogs(params: { action_type?: string; result?: string; page?: number } = {}) {
    await runFetch("Gagal memuat catatan aktivitas.", async () => {
      const res = await apiClient.get("/admin/audit-logs", {
        params: { action_type: params.action_type || undefined, result: params.result || undefined, page: params.page ?? 1, limit: 15 },
      });
      const d = res.data?.data;
      if (d) {
        logs.value = d.items || [];
        logsMeta.value = { total: d.total || 0, page: d.page || 1, limit: d.limit || 15, pages: d.pages || 1 };
      }
    });
  }

  async function fetchSystem() {
    await runFetch("Gagal memuat metrik kesehatan sistem.", async () => {
      const [resHealth, resExtras] = await Promise.all([
        apiClient.get("/admin/system-health"),
        apiClient.get("/admin/system-extras"),
      ]);
      if (resHealth.data?.data) health.value = resHealth.data.data;
      if (resExtras.data?.data) systemExtras.value = resExtras.data.data;
    });
  }

  return {
    loading,
    error,
    analytics,
    overviewExtras,
    health,
    systemExtras,
    users,
    usersMeta,
    invoices,
    invoiceSummary,
    invoicesMeta,
    logs,
    logsMeta,
    fetchOverview,
    fetchUsers,
    fetchInvoices,
    fetchLogs,
    fetchSystem,
  };
}
