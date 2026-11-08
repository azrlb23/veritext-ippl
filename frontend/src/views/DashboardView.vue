<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { DashboardStatsGrid, UploadDropzone, AuditProgressTracker, AuditActivityChart, AuditHistoryTable, type AuditTaskItem, type ActiveAuditTask } from "../components/dashboard";
import { useAuthStore } from "../stores/auth";
import { useNotification, usePolling } from "../composables";
import { documentService } from "../services/documentService";
import { auditService } from "../services/auditService";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const isUploading = ref(false);
const activeTab = ref<"all" | "upload" | "active" | "history">("all");
const tasks = ref<AuditTaskItem[]>([]);
const taskToCancel = ref<{ id: string; title: string } | null>(null);

const activeTasks = computed<ActiveAuditTask[]>(() =>
  tasks.value.filter((t) => t.status === "PROCESSING" || t.status === "QUEUED").map((t) => ({
    id: t.id, document_title: t.document_title, progress_pct: t.progress_pct,
    current_stage: t.current_stage || "Pemrosesan naskah...", audit_depth: t.audit_depth,
  }))
);

const completedCount = computed(() => tasks.value.filter((t) => t.status === "SUCCESS").length);

async function fetchTasks(): Promise<boolean> {
  if (!authStore.token) return true;
  try {
    const data = await auditService.getTasks(1, 20);
    if (data && Array.isArray(data.items)) {
      tasks.value = data.items.map((item) => ({
        id: item.task_id || item.id || "", document_title: item.document_title || "Naskah",
        audit_depth: item.audit_depth, status: item.status, progress_pct: item.progress_pct,
        score_composite: item.score_composite ?? null,
        created_at: item.created_at ? new Date(item.created_at).toLocaleDateString("id-ID") : "-",
      }));
    }
  } catch { /* ignore */ }
  return !tasks.value.some((t) => t.status === "PROCESSING" || t.status === "QUEUED");
}

const { start: startPolling } = usePolling(fetchTasks, { intervalMs: 2500, immediate: false });

onMounted(async () => {
  if (authStore.isAuthenticated) void authStore.fetchProfile();
  await fetchTasks();
  if (activeTasks.value.length > 0) startPolling();
});

async function handleStartAudit(payload: { file: File; depth: "FULL" | "TIER1_ONLY"; cost: number }) {
  const cost = payload.cost;
  if (authStore.tokenBalance < cost) {
    showNotification(`Saldo token tidak cukup (butuh ${cost}).`, "warning");
    router.push("/billing");
    return;
  }
  isUploading.value = true;
  try {
    await documentService.upload(payload.file, payload.depth);
    showNotification(`Naskah "${payload.file.name}" masuk antrean.`, "success");
    await authStore.fetchProfile();
    await fetchTasks();
    if (activeTasks.value.length > 0) startPolling();
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Gagal mengunggah.", "error");
  } finally {
    isUploading.value = false;
  }
}

async function confirmCancelTask() {
  if (!taskToCancel.value) return;
  const id = taskToCancel.value.id;
  taskToCancel.value = null;
  try {
    await auditService.cancelAudit(id);
    showNotification("Audit dibatalkan, token dikembalikan.", "info");
    await fetchTasks();
    await authStore.fetchProfile();
  } catch {
    showNotification("Gagal membatalkan tugas.", "error");
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans p-4 sm:p-8 space-y-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Ringkasan Audit Naskah</h1>
          <p class="text-xs sm:text-sm text-slate-500">Pantau proses pengujian orisinalitas dan riwayat evaluasi Anda</p>
        </div>
        <div class="inline-flex p-1 rounded-full bg-slate-200/70 text-xs font-semibold">
          <button v-for="tab in (['all', 'upload', 'active', 'history'] as const)" :key="tab" type="button" @click="activeTab = tab"
            class="px-3.5 py-1.5 rounded-full transition-all"
            :class="activeTab === tab ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'">
            {{ tab === 'all' ? 'Semua' : tab === 'upload' ? 'Unggah' : tab === 'active' ? `Antrean (${activeTasks.length})` : 'Riwayat' }}
          </button>
        </div>
      </div>

      <DashboardStatsGrid :tokenBalance="authStore.tokenBalance" :totalAudits="tasks.length" :completedAudits="completedCount" :inProgressAudits="activeTasks.length" @topup="router.push('/billing')" />

      <template v-if="activeTab === 'all'">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div class="lg:col-span-8"><UploadDropzone :isUploading="isUploading" :tokenBalance="authStore.tokenBalance" @startAudit="handleStartAudit" @topup="router.push('/billing')" /></div>
          <div class="lg:col-span-4"><AuditProgressTracker :activeTasks="activeTasks" @cancelTask="(id) => taskToCancel = { id, title: 'Naskah' }" @viewAll="activeTab = 'active'" /></div>
        </div>
        <AuditActivityChart />
        <AuditHistoryTable :tasks="tasks" @selectTask="(id) => router.push(`/audits/${id}`)" @cancelTask="(id) => taskToCancel = { id, title: 'Naskah' }" @refresh="fetchTasks" />
      </template>

      <UploadDropzone v-else-if="activeTab === 'upload'" :isUploading="isUploading" :tokenBalance="authStore.tokenBalance" @startAudit="handleStartAudit" @topup="router.push('/billing')" />
      <AuditProgressTracker v-else-if="activeTab === 'active'" :activeTasks="activeTasks" @cancelTask="(id) => taskToCancel = { id, title: 'Naskah' }" @viewAll="activeTab = 'active'" />
      <AuditHistoryTable v-else-if="activeTab === 'history'" :tasks="tasks" :isFullMode="true" @selectTask="(id) => router.push(`/audits/${id}`)" @cancelTask="(id) => taskToCancel = { id, title: 'Naskah' }" @refresh="fetchTasks" />
    </div>

    <div v-if="taskToCancel" class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl p-6 max-w-md w-full shadow-xl space-y-4">
        <h3 class="text-lg font-bold text-slate-900">Batalkan Tugas Audit?</h3>
        <p class="text-xs text-slate-600">Audit naskah akan dihentikan dan kuota token Anda akan dikembalikan otomatis.</p>
        <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <button type="button" @click="taskToCancel = null" class="px-4 py-2 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200">Kembali</button>
          <button type="button" @click="confirmCancelTask" class="px-4 py-2 rounded-full text-xs font-semibold bg-red-600 text-white hover:bg-red-700">Ya, Batalkan</button>
        </div>
      </div>
    </div>
  </div>
</template>
