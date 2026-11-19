import { computed, onMounted, ref } from "vue";
import { auditService } from "../services/auditService";
import { documentService } from "../services/documentService";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "./useNotification";
import { usePolling } from "./usePolling";

export interface AuditTaskRow {
  id: string;
  documentId: string;
  title: string;
  depth: string;
  status: string;
  progress: number;
  stage: string | null;
  score: number | null;
  createdAt: string;
}

const ACTIVE = ["QUEUED", "PROCESSING"];
export const isActiveStatus = (s: string) => ACTIVE.includes(s);
export const isFailedStatus = (s: string) => ["FAILED", "REVOKED", "CANCELLED"].includes(s);

export function useAuditTasks(limit = 20) {
  const authStore = useAuthStore();
  const { showNotification } = useNotification();
  const tasks = ref<AuditTaskRow[]>([]);
  const loading = ref(true);
  const page = ref(1);
  const pages = ref(1);
  const total = ref(0);

  const activeTasks = computed(() => tasks.value.filter((t) => isActiveStatus(t.status)));
  const doneTasks = computed(() => tasks.value.filter((t) => t.status === "SUCCESS"));

  async function fetchTasks(): Promise<boolean> {
    if (!authStore.token) return true;
    try {
      const data = await auditService.getTasks(page.value, limit);
      tasks.value = (data?.items ?? []).map((i: any) => ({
        id: i.task_id || i.id || "",
        documentId: i.document_id || "",
        title: i.document_title || "Naskah",
        depth: i.audit_depth,
        status: i.status,
        progress: i.progress_pct ?? 0,
        stage: i.current_stage ?? null,
        score: i.score_composite ?? null,
        createdAt: i.created_at ?? "",
      }));
      total.value = data?.total ?? tasks.value.length;
      pages.value = data?.pages ?? Math.max(1, Math.ceil(total.value / limit));
    } catch {
      /* jaringan terputus: tampilkan data terakhir */
    } finally {
      loading.value = false;
    }
    return activeTasks.value.length === 0;
  }

  const { start: startPolling } = usePolling(fetchTasks, { intervalMs: 2500, immediate: false });

  async function refresh() {
    await fetchTasks();
    if (activeTasks.value.length > 0) startPolling();
  }

  async function changePage(nextPage: number) {
    if (nextPage < 1 || nextPage > pages.value || nextPage === page.value) return;
    page.value = nextPage;
    loading.value = true;
    await refresh();
  }

  async function cancel(id: string) {
    try {
      await auditService.cancelAudit(id);
      showNotification("Pemeriksaan dibatalkan, token dikembalikan.", "info");
      await refresh();
      await authStore.fetchProfile();
    } catch {
      showNotification("Pemeriksaan tidak bisa dibatalkan.", "error");
    }
  }

  async function removeDocument(documentId: string) {
    if (!documentId) return;
    try {
      await documentService.delete(documentId);
      showNotification("Naskah dan seluruh riwayatnya telah dihapus permanen.", "success");
      if (tasks.value.length <= 1 && page.value > 1) page.value -= 1;
      await refresh();
    } catch {
      showNotification("Naskah tidak bisa dihapus.", "error");
    }
  }

  async function exportCsv() {
    try {
      await auditService.exportHistoryCsv();
      showNotification("Riwayat pemeriksaan berhasil diunduh.", "success");
    } catch {
      showNotification("Gagal mengunduh riwayat CSV.", "error");
    }
  }

  onMounted(refresh);
  return { tasks, loading, page, pages, total, activeTasks, doneTasks, refresh, changePage, cancel, removeDocument, exportCsv };
}

const STAGE_LABELS: Record<string, string> = {
  QUEUED: "Dalam antrean",
  INITIALIZING: "Menyiapkan naskah",
  LOADING_CORPUS_INDEX: "Membandingkan sumber",
  SAVING_AUDIT_REPORT: "Menyusun laporan",
};
export const stageLabel = (stage: string | null) => {
  if (!stage) return "Dalam antrean";
  return STAGE_LABELS[stage] ?? (/[a-z]/.test(stage) ? stage : "Memeriksa naskah");
};

export function formatDate(iso: string): string {
  if (!iso) return "-";
  return new Date(iso).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
}
