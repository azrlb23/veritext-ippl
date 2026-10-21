<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
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
const uploadDropzoneRef = ref<any>(null);
const promptInput = ref("");
const isPromptDragging = ref(false);
const activeViewTab = ref<"all" | "upload" | "active" | "history">("all");

const tasks = ref<AuditTaskItem[]>([]);
const totalTasksCount = ref(0);

const userInitials = computed(() => {
  const name = authStore.user?.full_name || "Mahasiswa";
  const parts = name.trim().split(" ");
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

const activeTasks = computed(() =>
  tasks.value
    .filter((t) => t.status === "PROCESSING" || t.status === "QUEUED")
    .map((t) => {
      let stage = "Menunggu antrean Celery worker...";
      if (t.progress_pct >= 70) {
        stage = "Tier 2 & 3: Penelusuran kemiripan semantik pgvector & Stilometri";
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

async function handlePromptSubmit() {
  if (activeViewTab.value !== "all" && activeViewTab.value !== "upload") {
    activeViewTab.value = "all";
    await nextTick();
  }
  if (uploadDropzoneRef.value?.triggerFilePicker) {
    uploadDropzoneRef.value.triggerFilePicker();
  } else {
    const el = document.getElementById("dashboardDocUpload");
    if (el) el.click();
  }
}

async function handlePromptFileDrop(event: DragEvent) {
  isPromptDragging.value = false;
  const files = event.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const file = files[0];
  const allowed = [".pdf", ".docx", ".txt"];
  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!allowed.includes(ext)) {
    showNotification(
      "Format berkas harus berupa .pdf, .docx, atau .txt.",
      "error",
      "Format Tidak Didukung"
    );
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    showNotification(
      "Ukuran berkas melebihi batas maksimum 50 MB.",
      "error",
      "Berkas Terlalu Besar"
    );
    return;
  }

  if (activeViewTab.value !== "all" && activeViewTab.value !== "upload") {
    activeViewTab.value = "all";
    await nextTick();
  }
  await handleStartAudit({ file, depth: "FULL" });
}

function handleAtMention() {
  if (!promptInput.value.includes("@korpus")) {
    promptInput.value = promptInput.value.trim() ? `${promptInput.value.trim()} @korpus ` : "@korpus ";
  }
}
</script>

<template>
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Ambient Warm Peach Radial Glow (Steep Signature Atmosphere) -->
    <div
      class="absolute top-0 left-1/2 -translate-x-1/2 -z-10 w-full max-w-6xl h-[480px] bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(251,225,209,0.55),rgba(255,255,255,0))] blur-3xl pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Editorial Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div class="space-y-2">
        <div class="flex flex-wrap items-center gap-2.5">
          <h1 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
            Workspace Audit Naskah
          </h1>
          <span
            v-if="authStore.user"
            class="text-xs px-3 py-0.5 font-medium rounded-full bg-[#f2f2f3] text-[#17191c] border border-[#ededed]"
          >
            {{ authStore.user.institution || 'VeriText Academic' }}
          </span>
          <span
            v-if="authStore.role === 'PREMIUM'"
            class="text-xs px-3 py-0.5 font-medium rounded-full bg-[#17191c] text-white border border-[#17191c]"
          >
            PREMIUM ACCOUNT
          </span>
          <span
            v-else-if="authStore.role === 'TRIAL'"
            class="text-xs px-3 py-0.5 font-medium rounded-full bg-[#fafafb] text-[#777b86] border border-[#ededed]"
          >
            TRIAL
          </span>
        </div>
        <p class="text-xs sm:text-sm text-[#777b86] font-normal leading-relaxed">
          Selamat datang, <strong class="italic font-medium text-[#17191c]">{{ authStore.user?.full_name || 'Peneliti Mahasiswa' }}</strong><span v-if="authStore.role === 'PREMIUM'" class="text-[#17191c] font-medium"> (Akun Premium)</span>. Kelola dan periksa naskah akademik dengan sistem deteksi hibrida berbasis <strong class="font-medium text-[#17191c]">pgvector HNSW &amp; Rabin-Karp</strong>.
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          type="button"
          @click="handleRefresh"
          class="inline-flex items-center space-x-1.5 px-4 py-2 rounded-full border border-[#ededed] bg-white hover:bg-[#fafafb] text-xs font-medium text-[#17191c] transition-colors shadow-sm active:scale-[0.98]"
        >
          <svg class="w-3.5 h-3.5 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Sinkronkan Status</span>
        </button>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- macOS Application Window Shell (Steep Signature Interface)   -->
    <!-- ============================================================ -->
    <div class="bg-white rounded-[24px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_25px_45px_-12px_rgba(0,0,0,0.08)] overflow-hidden">
      <!-- Window Title Bar -->
      <div class="bg-[#fafafb] px-5 py-3 border-b border-[#ededed] flex items-center justify-between select-none">
        <div class="flex items-center space-x-2">
          <!-- macOS 3 Window Controls -->
          <span class="w-3 h-3 rounded-full bg-[#ff5f56]/80 border border-[#e0443e]/40"></span>
          <span class="w-3 h-3 rounded-full bg-[#ffbd2e]/80 border border-[#dea123]/40"></span>
          <span class="w-3 h-3 rounded-full bg-[#27c93f]/80 border border-[#1aab29]/40"></span>
          <span class="text-xs text-[#777b86] font-mono ml-2">veritext-workspace / pipeline-v2.4</span>
        </div>
        <div class="flex items-center space-x-3 text-[11px] text-[#777b86]">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0] font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
            Worker Celery Terhubung
          </span>
          <span class="hidden sm:inline font-mono text-[10px]">pgvector: 384-dim</span>
        </div>
      </div>

      <!-- Window Body: Mist Gray Sidebar + Main Canvas -->
      <div class="flex flex-col lg:flex-row min-h-[640px]">
        <!-- Mist Gray Sidebar (#f2f2f3) -->
        <aside class="w-full lg:w-60 bg-[#f2f2f3] border-b lg:border-b-0 lg:border-r border-[#ededed] p-3 sm:p-4 flex flex-col justify-between gap-4">
          <div class="space-y-3 lg:space-y-4">
            <div class="px-2 pt-1 text-[10px] font-bold text-[#777b86] uppercase tracking-wider hidden lg:block">
              Navigasi Workspace
            </div>

            <!-- Structured Menu Items with Subtle Icons (Horizontal on Mobile, Vertical on Desktop) -->
            <nav class="flex flex-row lg:flex-col overflow-x-auto gap-1.5 lg:space-y-1 text-xs pb-1 lg:pb-0 scrollbar-none">
              <button
                type="button"
                @click="activeViewTab = 'all'"
                class="flex-shrink-0 lg:w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-colors font-medium"
                :class="activeViewTab === 'all' ? 'bg-white text-[#17191c] shadow-sm border border-[#ededed]' : 'text-[#777b86] hover:bg-white/60 hover:text-[#17191c]'"
              >
                <div class="flex items-center space-x-2.5">
                  <svg class="w-4 h-4 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                  <span class="whitespace-nowrap">Kanvas Utama</span>
                </div>
                <span class="text-[10px] tabular-nums font-mono px-1.5 py-0.5 rounded bg-[#e5e5e7] text-[#17191c] ml-2">
                  {{ totalTasksCount || tasks.length }}
                </span>
              </button>

              <button
                type="button"
                @click="activeViewTab = 'upload'"
                class="flex-shrink-0 lg:w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-colors font-medium"
                :class="activeViewTab === 'upload' ? 'bg-white text-[#17191c] shadow-sm border border-[#ededed]' : 'text-[#777b86] hover:bg-white/60 hover:text-[#17191c]'"
              >
                <div class="flex items-center space-x-2.5">
                  <svg class="w-4 h-4 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span class="whitespace-nowrap">Unggah Naskah</span>
                </div>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-[#fbe1d1] text-[#5d2a1a] font-medium ml-2">Dropzone</span>
              </button>

              <button
                type="button"
                @click="activeViewTab = 'active'"
                class="flex-shrink-0 lg:w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-colors font-medium"
                :class="activeViewTab === 'active' ? 'bg-white text-[#17191c] shadow-sm border border-[#ededed]' : 'text-[#777b86] hover:bg-white/60 hover:text-[#17191c]'"
              >
                <div class="flex items-center space-x-2.5">
                  <svg class="w-4 h-4 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="whitespace-nowrap">Antrean Deteksi</span>
                </div>
                <span v-if="activeTasks.length > 0" class="text-[10px] px-2 py-0.5 rounded-full bg-[#17191c] text-white tabular-nums font-mono ml-2">
                  {{ activeTasks.length }}
                </span>
              </button>

              <button
                type="button"
                @click="activeViewTab = 'history'"
                class="flex-shrink-0 lg:w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-colors font-medium"
                :class="activeViewTab === 'history' ? 'bg-white text-[#17191c] shadow-sm border border-[#ededed]' : 'text-[#777b86] hover:bg-white/60 hover:text-[#17191c]'"
              >
                <div class="flex items-center space-x-2.5">
                  <svg class="w-4 h-4 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span class="whitespace-nowrap">Riwayat Audit</span>
                </div>
                <span class="text-[10px] tabular-nums font-mono px-1.5 py-0.5 rounded bg-[#e5e5e7] text-[#17191c] ml-2">
                  {{ completedCount }}
                </span>
              </button>
            </nav>
          </div>

          <!-- Sidebar Quota Status Card (Desktop only; on mobile the DashboardStatsGrid provides this cleanly) -->
          <div class="hidden lg:block bg-white rounded-[20px] p-4 border border-[#ededed] shadow-sm space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-semibold text-[#777b86] uppercase tracking-wider">Saldo Token</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-[#fbe1d1] text-[#5d2a1a] font-semibold">Aktif</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-[#17191c] tabular-nums tracking-tight">
                {{ authStore.tokenBalance }} <span class="text-xs font-normal text-[#777b86]">Token</span>
              </div>
              <p class="text-[10px] text-[#777b86] mt-0.5">
                Mode Pay-as-you-go
              </p>
            </div>
            <button
              type="button"
              @click="handleTopup"
              class="w-full text-center py-2 px-3 rounded-full bg-[#17191c] hover:bg-[#2e3138] text-white text-xs font-medium transition-colors active:scale-[0.98]"
            >
              + Top Up Kuota
            </button>
          </div>
        </aside>

        <!-- Main Workspace Canvas -->
        <main class="flex-1 p-5 sm:p-8 space-y-6 bg-white overflow-y-auto">
          <!-- ============================================================ -->
          <!-- FLOATING AI PROMPT CALLOUT BAR (Steep Signature Component)   -->
          <!-- ============================================================ -->
          <div
            class="bg-white rounded-full pl-5 pr-2 py-2 border shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_15px_30px_-10px_rgba(0,0,0,0.07)] flex items-center gap-3 transition-colors duration-150"
            :class="isPromptDragging ? 'border-[#17191c] ring-2 ring-[#fbe1d1] bg-[#fafafb]' : 'border-[#ededed]'"
            @dragover.prevent="isPromptDragging = true"
            @dragleave.prevent="isPromptDragging = false"
            @drop.prevent="handlePromptFileDrop"
          >
            <div class="flex-1 flex items-center space-x-2">
              <svg class="w-4 h-4 text-[#777b86] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                v-model="promptInput"
                placeholder="Ketik pertanyaan naskah atau seret berkas ke dropzone..."
                @keydown.enter="handlePromptSubmit"
                aria-label="Input pertanyaan naskah atau seret berkas"
                class="w-full text-xs text-[#17191c] placeholder-[#a3a6af] bg-transparent focus:outline-none"
              />
            </div>

            <!-- @ Mention & History Clock Icon -->
            <div class="flex items-center space-x-2 text-[#777b86]">
              <button
                type="button"
                @click="handleAtMention"
                class="text-xs font-semibold cursor-pointer hover:text-[#17191c] px-1 transition-colors"
                title="Sisipkan mention filter (@korpus)"
                aria-label="Sisipkan mention filter korpus"
              >
                @
              </button>
              <button
                type="button"
                @click="activeViewTab = 'history'"
                class="hover:text-[#17191c] transition-colors p-1"
                title="Buka riwayat audit"
                aria-label="Buka riwayat audit"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </div>

            <!-- User Initials Pill Badge -->
            <div
              class="w-7 h-7 rounded-full bg-[#fbe1d1] text-[#5d2a1a] text-[11px] font-bold flex items-center justify-center flex-shrink-0 select-none"
              :title="authStore.user?.full_name || 'Pengguna'"
            >
              {{ userInitials }}
            </div>

            <!-- Round Black Arrow Submit Button -->
            <button
              type="button"
              @click="handlePromptSubmit"
              class="w-7 h-7 rounded-full bg-[#17191c] hover:bg-[#2e3138] text-white flex items-center justify-center flex-shrink-0 active:scale-[0.95] transition-transform duration-150 shadow-sm"
              title="Mulai audit naskah"
              aria-label="Mulai audit naskah"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>

          <!-- Stats Grid Artifacts -->
          <DashboardStatsGrid
            v-if="activeViewTab === 'all' || activeViewTab === 'upload'"
            :tokenBalance="authStore.tokenBalance"
            :totalAudits="totalTasksCount || tasks.length"
            :completedAudits="completedCount"
            :inProgressAudits="activeTasks.length"
            @topup="handleTopup"
          />

          <!-- Upload Dropzone -->
          <UploadDropzone
            v-if="activeViewTab === 'all' || activeViewTab === 'upload'"
            ref="uploadDropzoneRef"
            :isUploading="isUploading"
            @startAudit="handleStartAudit"
          />

          <!-- Active Tasks Progress Tracker -->
          <AuditProgressTracker
            v-if="(activeViewTab === 'all' || activeViewTab === 'active') && activeTasks.length > 0"
            :activeTasks="activeTasks"
            @cancelTask="handleCancelTask"
          />

          <!-- Empty State when Active Tab has no tasks -->
          <div
            v-if="activeViewTab === 'active' && activeTasks.length === 0"
            class="bg-[#fafafb] border border-[#ededed] rounded-[22px] p-8 text-center space-y-3"
          >
            <div class="w-10 h-10 rounded-full bg-white border border-[#ededed] text-[#777b86] flex items-center justify-center mx-auto shadow-sm">
              <svg class="w-5 h-5 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="text-xs font-semibold text-[#17191c]">Tidak Ada Antrean Deteksi Aktif</div>
            <p class="text-xs text-[#777b86] max-w-sm mx-auto">
              Semua proses audit telah selesai atau belum ada berkas yang diunggah ke antrean Celery worker.
            </p>
            <button
              type="button"
              @click="activeViewTab = 'upload'"
              class="inline-flex items-center space-x-1.5 px-4 py-1.5 rounded-full bg-[#17191c] hover:bg-[#2e3138] text-white text-xs font-medium transition-colors duration-150"
            >
              <span>Unggah Naskah Baru &rarr;</span>
            </button>
          </div>

          <!-- Pipeline Tier Legend -->
          <TierLegend v-if="activeViewTab === 'all'" />

          <!-- Recent Audits Table -->
          <AuditHistoryTable
            v-if="activeViewTab === 'all' || activeViewTab === 'history'"
            :tasks="tasks"
            @selectTask="navigateToReport"
            @refresh="handleRefresh"
          />
        </main>
      </div>
    </div>
  </div>
</template>
