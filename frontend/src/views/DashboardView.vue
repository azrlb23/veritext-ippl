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

const tasks = ref<AuditTaskItem[]>([
  {
    id: "task-001",
    document_title: "Pengaruh Algoritma Rekomendasi Terhadap Polaritas Opini Publik.pdf",
    audit_depth: "FULL",
    status: "SUCCESS",
    progress_pct: 100,
    score_composite: 21.4,
    created_at: "2026-10-11 19:45",
  },
  {
    id: "task-002",
    document_title: "Rancang Bangun Sistem Informasi Pelayanan Terpadu Satu Pintu.docx",
    audit_depth: "FULL",
    status: "PROCESSING",
    progress_pct: 70,
    score_composite: null,
    created_at: "2026-10-11 20:10",
  },
  {
    id: "task-003",
    document_title: "Tinjauan Literatur Etika Penggunaan Kecerdasan Buatan.txt",
    audit_depth: "TIER1_ONLY",
    status: "QUEUED",
    progress_pct: 0,
    score_composite: null,
    created_at: "2026-10-11 20:25",
  },
]);

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

// Worker polling simulation using usePolling composable: 0% -> 35% -> 70% -> 100%
const { start: startPolling } = usePolling(
  () => {
    let hasProcessing = false;
    for (const t of tasks.value) {
      if (t.status === "PROCESSING") {
        hasProcessing = true;
        if (t.progress_pct < 35) {
          t.progress_pct = 35;
        } else if (t.progress_pct < 70) {
          t.progress_pct = 70;
        } else if (t.progress_pct < 100) {
          t.progress_pct = 100;
          t.status = "SUCCESS";
          t.score_composite = +(Math.random() * 15 + 8).toFixed(1);
          showNotification(
            `Pengujian naskah "${t.document_title}" selesai (100%)! Skor komposit: ${t.score_composite}%.`,
            "success",
            "Audit Selesai"
          );
        }
      } else if (t.status === "QUEUED" && !hasProcessing) {
        t.status = "PROCESSING";
        t.progress_pct = 35;
        hasProcessing = true;
      }
    }

    const remainingActive = tasks.value.filter(
      (t) => t.status === "PROCESSING" || t.status === "QUEUED"
    );
    return remainingActive.length === 0;
  },
  { intervalMs: 2000, immediate: false }
);

onMounted(async () => {
  // Ensure profile is refreshed if token is present
  if (authStore.isAuthenticated) {
    void authStore.fetchProfile();
  }

  // Attempt to fetch user's real audit tasks from backend if token is available
  if (authStore.token && !authStore.token.startsWith("demo-")) {
    try {
      const data = await auditService.getTasks(1, 20);
      if (data && data.items && data.items.length > 0) {
        tasks.value = data.items.map((item) => ({
          id: item.task_id || item.id || `task-${Date.now()}`,
          document_title: item.document_title || "Naskah Akademik",
          audit_depth: item.audit_depth,
          status: item.status,
          progress_pct: item.progress_pct,
          score_composite: item.score_composite ?? null,
          created_at: new Date(item.created_at).toLocaleString("id-ID", {
            dateStyle: "short",
            timeStyle: "short",
          }),
        }));
      }
    } catch {
      // Offline fallback: keep mockup tasks
    }
  }

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
  let taskId = `task-${Date.now().toString().slice(-4)}`;

  try {
    if (authStore.token && !authStore.token.startsWith("demo-")) {
      const res = await documentService.upload(payload.file, payload.depth);
      if (res && res.task_id) {
        taskId = String(res.task_id);
      }
      void authStore.fetchProfile();
    }
  } catch (err: any) {
    if (err?.response) {
      const errorMsg =
        err.response.data?.detail || err.response.data?.message || "Gagal mengunggah naskah.";
      const statusTitle = err.response.status === 402 ? "Kredit Tidak Cukup" : "Gagal Mengunggah";
      const variant = err.response.status === 402 ? "warning" : "error";
      showNotification(errorMsg, variant, statusTitle);
      if (err.response.status === 402) {
        router.push("/billing");
      }
      return;
    }
    // Offline demo fallback notice
    showNotification("Mode Demo: Menggunakan antrean lokal karena backend offline.", "info", "Demo Mode");
  } finally {
    isUploading.value = false;
  }

  // Deduct token from reactive wallet
  authStore.decrementTokenBalance(tokenCost);

  // Add task to active queue
  const newTask: AuditTaskItem = {
    id: taskId,
    document_title: payload.file.name,
    audit_depth: payload.depth,
    status: "PROCESSING",
    progress_pct: 0,
    score_composite: null,
    created_at: "Baru saja",
  };
  tasks.value.unshift(newTask);

  showNotification(
    `Naskah "${payload.file.name}" berhasil diunggah (${payload.depth}) dan sedang diproses oleh Celery worker pipeline.`,
    "success",
    "Pengujian Dimulai"
  );

  startPolling();
}

async function handleCancelTask(taskId: string) {
  const task = tasks.value.find((t) => t.id === taskId);
  if (task) {
    task.status = "CANCELLED";
    if (authStore.token && !authStore.token.startsWith("demo-")) {
      try {
        await auditService.cancelAudit(taskId);
      } catch {
        // Continue
      }
    }
    showNotification(`Tugas audit ${taskId} berhasil dibatalkan.`, "info");
  }
}

function navigateToReport(taskId: string) {
  router.push(`/audits/${taskId}`);
}

function handleTopup() {
  router.push("/billing");
}

async function handleRefresh() {
  if (authStore.token && !authStore.token.startsWith("demo-")) {
    try {
      const data = await auditService.getTasks(1, 20);
      if (data && data.items && data.items.length > 0) {
        tasks.value = data.items.map((item) => ({
          id: item.task_id || item.id || `task-${Date.now()}`,
          document_title: item.document_title || "Naskah Akademik",
          audit_depth: item.audit_depth,
          status: item.status,
          progress_pct: item.progress_pct,
          score_composite: item.score_composite ?? null,
          created_at: new Date(item.created_at).toLocaleString("id-ID", {
            dateStyle: "short",
            timeStyle: "short",
          }),
        }));
      }
      await authStore.fetchProfile();
    } catch {
      // Keep existing
    }
  }
  startPolling();
  showNotification("Memperbarui status tugas dari antrean Celery worker...", "info");
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
      </div>
      <p class="text-xs sm:text-sm text-audyr-ash mt-1 font-normal">
        Selamat datang, <strong class="italic font-bold text-[#262626]">{{ authStore.user?.full_name || 'Peneliti Mahasiswa' }}</strong>. Unggah dokumen akademik untuk diproses oleh <strong class="font-bold text-[#262626]">4-Tier Hybrid Detection Pipeline</strong>.
      </p>
    </div>

    <!-- Stats Grid -->
    <DashboardStatsGrid
      :tokenBalance="authStore.tokenBalance"
      :totalAudits="tasks.length"
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
