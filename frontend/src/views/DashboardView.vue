<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import TierLegend from "../components/TierLegend.vue";
import {
  DashboardStatsGrid,
  UploadDropzone,
  AuditProgressTracker,
  AuditHistoryTable,
  type AuditTaskItem,
} from "../components/dashboard";
import { useAuthStore } from "../stores/auth";
import { useNotification, usePolling } from "../composables";
import { documentService } from "../services/documentService";
import { auditService } from "../services/auditService";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const isUploading = ref(false);

const tasks = ref<AuditTaskItem[]>([]);
const totalTasksCount = ref(0);

const activeTasks = computed(() =>
  tasks.value
    .filter((t) => t.status === "PROCESSING" || t.status === "QUEUED")
    .map((t) => {
      let stage = "Menunggu antrean Celery worker...";
      if (t.progress_pct >= 70) {
        stage = "Tier 2 & 3: Penelusuran kemiripan semantik pgvector & Stylometri";
      } else if (t.progress_pct >= 35) {
        stage = "Tier 1: Ekstraksi N-Gram & Rabin-Karp Winnowing leksikal";
      } else if (t.status === "PROCESSING") {
        stage = "Inisialisasi parser naskah & ekstraksi struktur teks...";
      }
      return {
        id: t.id,
        document_title: t.document_title,
        progress_pct: t.progress_pct,
        current_stage: stage,
        audit_depth: t.audit_depth,
      };
    })
);

const completedCount = computed(
  () => tasks.value.filter((t) => t.status === "SUCCESS").length
);

async function fetchTasks(): Promise<boolean> {
  if (!authStore.token) return true;
  try {
    const data = await auditService.getTasks(1, 20);
    if (data && Array.isArray(data.items)) {
      totalTasksCount.value = typeof data.total === "number" ? data.total : data.items.length;
      const prevTasks = new Map(tasks.value.map((t) => [t.id, t.status]));
      tasks.value = data.items.map((item) => ({
        id: item.task_id || item.id || "",
        document_title: item.document_title || "Naskah Akademik",
        audit_depth: item.audit_depth,
        status: item.status,
        progress_pct: item.progress_pct,
        score_composite: item.score_composite ?? null,
        created_at: item.created_at
          ? new Date(item.created_at).toLocaleString("id-ID", {
              dateStyle: "short",
              timeStyle: "short",
            })
          : "-",
      }));

      // Notify on finished tasks
      for (const t of tasks.value) {
        const prevStatus = prevTasks.get(t.id);
        if (
          (prevStatus === "PROCESSING" || prevStatus === "QUEUED") &&
          t.status === "SUCCESS"
        ) {
          showNotification(
            `Pengujian naskah "${t.document_title}" selesai (100%)! Skor komposit: ${t.score_composite ?? 0}%.`,
            "success",
            "Audit Selesai"
          );
          void authStore.fetchProfile();
        } else if (
          (prevStatus === "PROCESSING" || prevStatus === "QUEUED") &&
          t.status === "FAILED"
        ) {
          showNotification(
            `Pengujian naskah "${t.document_title}" gagal diproses oleh worker.`,
            "error",
            "Audit Gagal"
          );
        }
      }
    }
  } catch (err: any) {
    console.error("Gagal memuat tugas audit:", err);
  }

  const hasActive = tasks.value.some((t) => t.status === "PROCESSING" || t.status === "QUEUED");
  return !hasActive;
}

// Real polling from backend Celery tasks
const { start: startPolling } = usePolling(
  async () => {
    return await fetchTasks();
  },
  { intervalMs: 2500, immediate: false }
);

onMounted(async () => {
  if (authStore.isAuthenticated) {
    void authStore.fetchProfile();
  }
  await fetchTasks();
  if (activeTasks.value.length > 0) {
    startPolling();
  }
});

async function handleStartAudit(payload: { file: File; depth: "FULL" | "TIER1_ONLY" }) {
  const tokenCost = payload.depth === "FULL" ? 2 : 1;
  if (authStore.tokenBalance < tokenCost) {
    showNotification(
      `Saldo token Anda tidak mencukupi untuk audit ${payload.depth} (${tokenCost} token diperlukan). Silakan lakukan top up.`,
      "warning",
      "Kredit Tidak Cukup"
    );
    router.push("/billing");
    return;
  }

  isUploading.value = true;
  try {
    await documentService.upload(payload.file, payload.depth);
    showNotification(
      `Naskah "${payload.file.name}" berhasil diunggah (${payload.depth}) dan sedang diproses oleh Celery worker pipeline.`,
      "success",
      "Pengujian Dimulai"
    );
    await authStore.fetchProfile();
    await fetchTasks();
    if (activeTasks.value.length > 0) {
      startPolling();
    }
  } catch (err: any) {
    const errorMsg =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      "Gagal mengunggah naskah.";
    const statusTitle = err?.response?.status === 402 ? "Kredit Tidak Cukup" : "Gagal Mengunggah";
    const variant = err?.response?.status === 402 ? "warning" : "error";
    showNotification(errorMsg, variant, statusTitle);
    if (err?.response?.status === 402) {
      router.push("/billing");
    }
  } finally {
    isUploading.value = false;
  }
}

async function handleCancelTask(taskId: string) {
  try {
    await auditService.cancelAudit(taskId);
    showNotification(`Tugas audit ${taskId} berhasil dibatalkan.`, "info");
    await fetchTasks();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal membatalkan tugas audit.",
      "error"
    );
  }
}

function navigateToReport(taskId: string) {
  router.push(`/audits/${taskId}`);
}

function handleTopup() {
  router.push("/billing");
}

async function handleRefresh() {
  showNotification("Memperbarui status tugas dari antrean Celery worker...", "info");
  await fetchTasks();
  await authStore.fetchProfile();
  if (activeTasks.value.length > 0) {
    startPolling();
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Header -->
    <div>
      <div class="flex flex-wrap items-center gap-2.5">
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#262626] tracking-tight">
          Workspace Audit Naskah
        </h1>
        <span
          v-if="authStore.user"
          class="text-xs px-2.5 py-0.5 font-bold rounded-full bg-[#ededed] text-[#262626] border border-[#ededed]"
        >
          {{ authStore.user.institution || 'VeriText Academic' }}
        </span>
        <span
          v-if="authStore.role === 'PREMIUM'"
          class="text-xs px-2.5 py-0.5 font-black rounded-full bg-[#262626] text-white border border-[#262626]"
        >
          PREMIUM ACCOUNT
        </span>
        <span
          v-else-if="authStore.role === 'TRIAL'"
          class="text-xs px-2.5 py-0.5 font-bold rounded-full bg-[#fafafa] text-[#737373] border border-[#ededed]"
        >
          TRIAL
        </span>
      </div>
      <p class="text-xs sm:text-sm text-audyr-ash mt-1 font-normal">
        Selamat datang, <strong class="italic font-bold text-[#262626]">{{ authStore.user?.full_name || 'Peneliti Mahasiswa' }}</strong><span v-if="authStore.role === 'PREMIUM'" class="text-[#262626] font-bold"> (Akun Premium)</span>. Unggah dokumen akademik untuk diproses oleh <strong class="font-bold text-[#262626]">4-Tier Hybrid Detection Pipeline</strong>.
      </p>
    </div>

    <!-- Stats Grid -->
    <DashboardStatsGrid
      :tokenBalance="authStore.tokenBalance"
      :totalAudits="totalTasksCount || tasks.length"
      :completedAudits="completedCount"
      :inProgressAudits="activeTasks.length"
      @topup="handleTopup"
    />

    <!-- Upload Dropzone -->
    <UploadDropzone
      :isUploading="isUploading"
      @startAudit="handleStartAudit"
    />

    <!-- Active Tasks Progress Tracker -->
    <AuditProgressTracker
      :activeTasks="activeTasks"
      @cancelTask="handleCancelTask"
    />

    <!-- Pipeline Tier Legend -->
    <TierLegend />

    <!-- Recent Audits Table -->
    <AuditHistoryTable
      :tasks="tasks"
      @selectTask="navigateToReport"
      @refresh="handleRefresh"
    />
  </div>
</template>
