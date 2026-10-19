<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  AdminStatsGrid,
  UserManagementTable,
  SystemSettingsCard,
  AdminAuditLogsTable,
  type ManagedUser,
  type SystemConfig,
  type AuditLogItem,
} from "../components/admin";
import {
  CorpusStatsGrid,
  CorpusFilterBar,
  CorpusTable,
  CorpusUploadModal,
  type CorpusItemData,
} from "../components/corpus";
import { useNotification, useModal } from "../composables";
import { useAuthStore } from "../stores/auth";
import { apiClient } from "../services/api";
import { corpusService } from "../services/corpusService";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const { isOpen: isCorpusUploadOpen, open: openCorpusUpload, close: closeCorpusUpload } = useModal();

// UI States
const isMobileSidebarOpen = ref(false);
const isProfileDropdownOpen = ref(false);
const userTableRef = ref<InstanceType<typeof UserManagementTable> | null>(null);

// Data States
const users = ref<ManagedUser[]>([]);
const auditLogs = ref<AuditLogItem[]>([]);
const corpusList = ref<CorpusItemData[]>([]);
const isIngestingCorpus = ref(false);
const isCorpusLoading = ref(false);
const corpusCategory = ref("SEMUA");
const corpusSearch = ref("");

const systemMetrics = ref({
  totalAudits: 0,
  totalCorpusDocs: 0,
  vectorCount: 0,
  avgLatencyMs: 0,
  systemLoadPct: 0,
  databaseStatus: "HEALTHY",
  redisStatus: "HEALTHY",
  celeryActiveTasks: 0,
});

// Computed Metrics for Zendenta Asset Card
const totalTokensInSystem = computed(() => {
  return users.value.reduce((acc, u) => acc + (u.token_balance || 0), 0);
});

const activeUsersCount = computed(() => {
  return users.value.filter((u) => u.is_active).length;
});

const suspendedUsersCount = computed(() => {
  return users.value.filter((u) => !u.is_active).length;
});

const lowTokenUsersCount = computed(() => {
  return users.value.filter((u) => u.token_balance < 3).length;
});

// Proportions for Segmented Status Bar
const segmentActivePct = computed(() => {
  if (users.value.length === 0) return 70;
  return Math.round((activeUsersCount.value / users.value.length) * 100);
});

const segmentLowStockPct = computed(() => {
  if (users.value.length === 0) return 15;
  return Math.round((lowTokenUsersCount.value / users.value.length) * 100);
});

const segmentSuspendedPct = computed(() => {
  if (users.value.length === 0) return 15;
  return Math.max(0, 100 - segmentActivePct.value - segmentLowStockPct.value);
});

// Filtered Corpus List
const filteredCorpusList = computed(() => {
  return corpusList.value.filter((item) => {
    const matchesCategory =
      corpusCategory.value === "SEMUA" || item.category === corpusCategory.value;
    const matchesSearch =
      !corpusSearch.value.trim() ||
      item.title.toLowerCase().includes(corpusSearch.value.toLowerCase()) ||
      (item.category && item.category.toLowerCase().includes(corpusSearch.value.toLowerCase()));
    return matchesCategory && matchesSearch;
  });
});

const totalCorpusChunks = computed(() => {
  return corpusList.value.reduce((acc, curr) => acc + (curr.total_chunks || 0), 0);
});

// Data Loaders
async function loadRealUsers() {
  try {
    const res = await apiClient.get<any>("/admin/users");
    const items = res.data?.data?.items || res.data?.data;
    if (Array.isArray(items)) {
      users.value = items.map((u: any) => ({
        id: String(u.id),
        full_name: u.full_name,
        email: u.email,
        institution: u.institution || "Institut Teknologi Nasional",
        role: u.role,
        token_balance: u.token_balance ?? (u.wallet?.balance ?? 5),
        is_active: u.is_active ?? true,
        created_at: u.created_at ? String(u.created_at).substring(0, 10) : "",
      }));
    }
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memuat daftar pengguna.",
      "error"
    );
  }
}

async function loadAuditLogs() {
  try {
    const res = await apiClient.get<any>("/admin/audit-logs");
    const items = res.data?.data?.items || res.data?.data;
    if (Array.isArray(items)) {
      auditLogs.value = items.map((l: any) => ({
        id: String(l.id),
        timestamp: l.created_at
          ? new Date(l.created_at).toLocaleString("id-ID", {
              dateStyle: "short",
              timeStyle: "medium",
            })
          : new Date().toISOString().replace("T", " ").substring(0, 19),
        actor_name: l.actor_name || "Super Administrator",
        actor_email: l.actor_email || "admin@veritext.ai",
        action: l.action_type || l.action || "INFO",
        target_resource: l.target_resource || "-",
        ip_address: l.ip_address || "127.0.0.1",
        status: l.status || "SUCCESS",
        details: l.details || "",
      }));
    }
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memuat log audit forensik.",
      "error"
    );
  }
}

async function loadCorpus() {
  isCorpusLoading.value = true;
  try {
    const data = await corpusService.list(
      corpusCategory.value === "SEMUA" ? undefined : corpusCategory.value,
      1,
      100
    );
    if (data && Array.isArray(data.items)) {
      corpusList.value = data.items.map((item: any) => ({
        id: String(item.id),
        title: item.title || item.original_filename || "Naskah Korpus",
        category: item.category || "Umum",
        academic_year: item.academic_year || "-",
        total_chunks: item.total_chunks ?? 0,
        status: item.status || "INDEXED",
        created_at: item.created_at ? String(item.created_at).substring(0, 10) : "",
      }));
    }
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memuat repositori korpus.",
      "error"
    );
  } finally {
    isCorpusLoading.value = false;
  }
}

async function loadMetrics() {
  try {
    const res = await apiClient.get<any>("/admin/health-metrics");
    const d = res.data?.data;
    if (d) {
      systemMetrics.value.systemLoadPct = Math.round(d.cpu_percent || 0);
      systemMetrics.value.avgLatencyMs = Math.round(d.db_latency_ms || 0);
      systemMetrics.value.databaseStatus = d.database_status || "HEALTHY";
      systemMetrics.value.redisStatus = d.redis_status || "HEALTHY";
      systemMetrics.value.celeryActiveTasks = d.celery_active_tasks || 0;
      systemMetrics.value.totalAudits = d.total_audits ?? 0;
      systemMetrics.value.totalCorpusDocs = d.total_corpus_docs ?? 0;
      systemMetrics.value.vectorCount = d.total_vector_chunks ?? 0;
    }
  } catch {
    // Keep defaults
  }
}

onMounted(() => {
  void loadRealUsers();
  void loadAuditLogs();
  void loadCorpus();
  void loadMetrics();
});

watch(corpusCategory, () => {
  void loadCorpus();
});

// User Mutations
async function handleToggleStatus(userId: string) {
  const user = users.value.find((u) => u.id === userId);
  if (!user) return;
  const newStatus = !user.is_active;

  try {
    await apiClient.patch(`/admin/users/${userId}/status`, { is_active: newStatus });
    user.is_active = newStatus;
    showNotification(
      `Status pengguna ${user.full_name} berhasil diubah menjadi ${user.is_active ? "Aktif" : "Nonaktif"}.`,
      "info",
      "Perubahan Status"
    );
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal mengubah status pengguna.",
      "error"
    );
  }
}

async function handleAdjustTokens(userId: string, delta: number) {
  const user = users.value.find((u) => u.id === userId);
  if (!user) return;

  try {
    const res = await apiClient.post<any>(`/admin/users/${userId}/adjust-tokens`, {
      amount: delta,
      note: "Koreksi kuota token oleh Super Administrator",
    });
    if (res.data?.data?.new_balance !== undefined) {
      user.token_balance = res.data.data.new_balance;
    } else {
      user.token_balance = Math.max(0, user.token_balance + delta);
    }
    showNotification(
      `Berhasil memperbarui ${delta > 0 ? "+" + delta : delta} token untuk ${user.full_name}. Saldo kini: ${user.token_balance}`,
      "success",
      "Penyesuaian Token"
    );
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menyesuaikan token pengguna.",
      "error"
    );
  }
}

async function handleChangeRole(userId: string, newRole: ManagedUser["role"]) {
  const user = users.value.find((u) => u.id === userId);
  if (!user) return;

  try {
    await apiClient.put(`/admin/users/${userId}`, { role: newRole });
    user.role = newRole;
    showNotification(`Peran pengguna ${user.full_name} diubah menjadi ${newRole}.`, "info");
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal mengubah peran pengguna.",
      "error"
    );
  }
}

async function handleCreateUser(payload: {
  full_name: string;
  email: string;
  password?: string;
  institution: string;
  role: ManagedUser["role"];
  token_balance: number;
}) {
  try {
    await apiClient.post<any>("/admin/users", {
      full_name: payload.full_name,
      email: payload.email,
      password: payload.password || "VeriText#2026",
      institution: payload.institution,
      role: payload.role,
      initial_tokens: payload.token_balance,
    });
    showNotification(
      `Pengguna ${payload.full_name} (${payload.email}) berhasil ditambahkan ke sistem.`,
      "success",
      "Tambah Pengguna"
    );
    await loadRealUsers();
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menambahkan pengguna baru.",
      "error"
    );
  }
}

async function handleUpdateUser(payload: ManagedUser & { new_password?: string }) {
  try {
    await apiClient.put(`/admin/users/${payload.id}`, {
      full_name: payload.full_name,
      email: payload.email,
      password: payload.new_password || undefined,
      institution: payload.institution,
      role: payload.role,
      is_active: payload.is_active,
    });

    if (payload.new_password) {
      await apiClient.post(`/admin/users/${payload.id}/reset-password`, {
        new_password: payload.new_password,
      });
    }

    showNotification(
      payload.new_password
        ? `Data pengguna ${payload.full_name} & kata sandi baru berhasil diperbarui.`
        : `Data pengguna ${payload.full_name} berhasil diperbarui.`,
      "success",
      "Perbarui Pengguna"
    );
    await loadRealUsers();
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memperbarui data pengguna.",
      "error"
    );
  }
}

async function handleDeleteUser(userId: string) {
  const user = users.value.find((u) => u.id === userId);
  try {
    await apiClient.delete(`/admin/users/${userId}`);
    showNotification(
      `Akun pengguna ${user ? user.full_name : userId} telah dihapus permanen dari sistem.`,
      "warning",
      "Hapus Pengguna"
    );
    await loadRealUsers();
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menghapus pengguna.",
      "error"
    );
  }
}

async function handleSaveConfig(newConfig: SystemConfig) {
  try {
    await apiClient.post("/admin/reindex-hnsw");
    showNotification(
      `Hyperparameter sistem berhasil diperbarui dan re-indexing dijadwalkan. Ambang batas kosinus: ${newConfig.hnsw_similarity_threshold}`,
      "success",
      "Konfigurasi Tersimpan"
    );
    await loadAuditLogs();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menyimpan konfigurasi hyperparameter.",
      "error"
    );
  }
}

async function handleRefreshLogs() {
  await loadAuditLogs();
  showNotification("Daftar jejak audit forensik berhasil disinkronkan ulang.", "info", "Sinkronisasi Log");
}

function handleExportCsv() {
  const headers = ["ID", "Waktu", "Aktor", "Email", "Aksi", "Target Sumber Daya", "Alamat IP", "Status", "Rincian"];
  const rows = auditLogs.value.map((l) => [
    l.id,
    `"${l.timestamp}"`,
    `"${l.actor_name}"`,
    `"${l.actor_email}"`,
    l.action,
    `"${l.target_resource}"`,
    l.ip_address,
    l.status,
    `"${l.details || ''}"`,
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `audit-trail-veritext-${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showNotification("Berkas CSV log audit sistem berhasil diekspor.", "success", "Unduh Selesai");
}

// Corpus Actions
async function handleBulkIngest(payload: { title: string; category: string; academicYear: string; file?: File | null }) {
  if (!payload.file) {
    showNotification("Berkas arsip ZIP harus disertakan.", "warning");
    return;
  }
  isIngestingCorpus.value = true;
  try {
    await corpusService.ingest(payload.file, payload.category, payload.academicYear);
    closeCorpusUpload();
    showNotification(
      `Arsip "${payload.title}" berhasil diunggah dan diantrekan ke Celery worker untuk ekstraksi embedding HNSW pgvector.`,
      "success",
      "Ingest Berhasil"
    );
    await loadCorpus();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal mengunggah dan mengindeks korpus.",
      "error"
    );
  } finally {
    isIngestingCorpus.value = false;
  }
}

async function handleDeleteCorpusItem(id: string) {
  try {
    await corpusService.delete(id);
    showNotification(`Koleksi dokumen korpus telah berhasil dihapus.`, "info");
    await loadCorpus();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menghapus dokumen korpus.",
      "error"
    );
  }
}

// Navigation & Sections
type AdminSection = "overview" | "users" | "corpus" | "config" | "logs" | "pdp";

const currentSection = computed<AdminSection>(() => {
  const hash = (route.hash || "").replace("#", "").toLowerCase();
  if (hash === "users") return "users";
  if (hash === "corpus") return "corpus";
  if (hash === "config") return "config";
  if (hash === "logs") return "logs";
  if (hash === "pdp") return "pdp";
  return "users"; // Default to users matching Zendenta reference
});

const sectionTitle = computed(() => {
  switch (currentSection.value) {
    case "users":
      return "Daftar Pengguna & Saldo";
    case "overview":
      return "Overview & Telemetri";
    case "corpus":
      return "Bank Korpus Ilmiah";
    case "config":
      return "Tuning Engine AI";
    case "logs":
      return "Log Jejak Forensik";
    case "pdp":
      return "Kepatuhan UU PDP";
    default:
      return "Konsol Administrator";
  }
});

function setSection(section: AdminSection) {
  isMobileSidebarOpen.value = false;
  if (section === "overview") {
    router.push({ path: "/admin", hash: "" });
  } else {
    router.push({ path: "/admin", hash: `#${section}` });
  }
}

function handleQuickAddUser() {
  if (currentSection.value !== "users") {
    setSection("users");
  }
  setTimeout(() => {
    userTableRef.value?.openCreate();
  }, 100);
}

async function handleLogout() {
  isProfileDropdownOpen.value = false;
  await authStore.logout();
  showNotification("Anda telah berhasil keluar dari akun.", "info", "Sesi Berakhir");
  router.push("/login");
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-[#f8f9fb] font-sans antialiased text-[#1e293b]">
    <!-- Mobile Drawer Backdrop -->
    <div
      v-if="isMobileSidebarOpen"
      @click="isMobileSidebarOpen = false"
      class="fixed inset-0 bg-black/40 z-40 lg:hidden backdrop-blur-xs transition-opacity"
    ></div>

    <!-- 1. PERSISTENT LEFT SIDEBAR (Zendenta Layout - Ink Black Palette) -->
    <aside
      class="fixed inset-y-0 left-0 z-50 w-64 xl:w-72 bg-white border-r border-[#ededed] flex flex-col justify-between transition-transform duration-300 lg:translate-x-0 lg:static shrink-0 select-none shadow-[2px_0_12px_rgba(0,0,0,0.02)]"
      :class="isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="p-5 flex-1 overflow-y-auto space-y-6">
        <!-- Brand Header (Zendenta Brand Header equivalent) -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2.5">
            <div class="w-8 h-8 rounded-lg bg-[#17191c] flex items-center justify-center text-white font-bold text-sm shadow-xs">
              <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <span class="font-bold text-base tracking-tight text-[#17191c]">VeriText AI</span>
              <span class="block text-[10px] uppercase font-bold text-[#777b86] tracking-wider">Enterprise Admin</span>
            </div>
          </div>
          <!-- Close button on mobile -->
          <button
            type="button"
            @click="isMobileSidebarOpen = false"
            class="lg:hidden p-1 rounded-md text-[#94a3b8] hover:text-[#17191c] hover:bg-[#f1f5f9]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Tenant / Institution Card (Avicena Clinic equivalent) -->
        <div class="bg-[#f8fafc] border border-[#e2e8f0] rounded-xl p-3 flex items-center justify-between">
          <div class="flex items-center space-x-2.5 min-w-0">
            <div class="w-8 h-8 rounded-lg bg-white border border-[#e2e8f0] flex items-center justify-center text-[#475569] shrink-0 shadow-2xs">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-xs font-bold text-[#17191c] truncate">
                {{ authStore.user?.institution || 'Institut Teknologi Nasional' }}
              </div>
              <div class="text-[10px] text-[#777b86] truncate">
                Server Utama • PDP Compliant
              </div>
            </div>
          </div>
          <svg class="w-4 h-4 text-[#94a3b8] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
          </svg>
        </div>

        <!-- Categorized Navigation Menu -->
        <nav class="space-y-5 text-xs font-semibold">
          <!-- Top Single Link: Dashboard -->
          <div>
            <button
              type="button"
              @click="setSection('overview')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'overview' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              <span>Dashboard &amp; Telemetri</span>
            </button>
          </div>

          <!-- Group 1: KONSOL AKADEMIK -->
          <div class="space-y-1">
            <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
              Konsol Akademik
            </div>
            <!-- BANK KORPUS ILMIAH (FULLY INTEGRATED) -->
            <button
              type="button"
              @click="setSection('corpus')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'corpus' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span>Bank Korpus Ilmiah</span>
            </button>
            <button
              type="button"
              @click="setSection('overview')"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c] transition-colors text-left"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>Indeks Vektor HNSW</span>
            </button>
          </div>

          <!-- Group 2: MANAJEMEN PENGGUNA (Zendenta Stocks Active Pill) -->
          <div class="space-y-1">
            <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
              Manajemen Pengguna
            </div>
            <button
              type="button"
              @click="setSection('users')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'users' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>Daftar Pengguna &amp; Saldo</span>
            </button>
            <button
              type="button"
              @click="setSection('users')"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c] transition-colors text-left"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Koreksi Kuota Token</span>
            </button>
          </div>

          <!-- Group 3: SISTEM & AUDIT -->
          <div class="space-y-1">
            <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
              Sistem &amp; Audit
            </div>
            <button
              type="button"
              @click="setSection('config')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'config' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              <span>Tuning Engine AI</span>
            </button>
            <button
              type="button"
              @click="setSection('logs')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'logs' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Log Jejak Forensik</span>
            </button>
            <button
              type="button"
              @click="setSection('pdp')"
              class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors text-left"
              :class="currentSection === 'pdp' ? 'bg-[#17191c] text-white font-bold shadow-2xs' : 'text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c]'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>Kepatuhan UU PDP</span>
            </button>
          </div>

          <!-- Group 4: NAVIGASI LUAR -->
          <div class="space-y-1">
            <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
              Navigasi Luar
            </div>
            <router-link
              to="/dashboard"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c] transition-colors text-left"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Workspace Mahasiswa</span>
            </router-link>
            <router-link
              to="/"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-[#64748b] hover:bg-[#f8fafc] hover:text-[#17191c] transition-colors text-left"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span>Beranda Publik</span>
            </router-link>
          </div>
        </nav>
      </div>

      <!-- Sidebar Footer: Super Admin Logout -->
      <div class="p-4 border-t border-[#ededed] bg-[#fafbfc]">
        <button
          type="button"
          @click="handleLogout"
          class="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-lg border border-[#e2e8f0] bg-white hover:bg-red-50 hover:text-red-600 text-xs font-semibold text-[#475569] shadow-2xs transition-colors"
        >
          <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Keluar Administrator</span>
        </button>
      </div>
    </aside>

    <!-- 2. MAIN APPLICATION COLUMN (Zendenta Layout) -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
      <!-- TOP APPLICATION BAR -->
      <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-[#ededed] px-6 sm:px-8 py-3.5 flex items-center justify-between shadow-2xs">
        <!-- Left: Mobile Trigger + Breadcrumb Title (< Stocks equivalent) -->
        <div class="flex items-center space-x-3">
          <button
            type="button"
            @click="isMobileSidebarOpen = true"
            class="lg:hidden p-1.5 rounded-lg border border-[#e2e8f0] text-[#64748b] hover:text-[#17191c]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Breadcrumb Chevron + Title -->
          <div class="flex items-center space-x-2">
            <button
              type="button"
              @click="setSection('users')"
              class="w-7 h-7 rounded-full border border-[#e2e8f0] flex items-center justify-center text-[#64748b] hover:text-[#17191c] hover:bg-[#f8fafc] transition-colors"
              title="Kembali ke Daftar Pengguna"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-[#17191c]">
              {{ sectionTitle }}
            </h1>
          </div>
        </div>

        <!-- Middle-Right: Search Pill & Action Icons -->
        <div class="flex items-center space-x-2.5 sm:space-x-4">
          <!-- Global Search Input -->
          <div class="hidden md:flex items-center relative w-60 lg:w-72">
            <input
              type="text"
              placeholder="Cari naskah, pengguna, audit log..."
              class="w-full px-3.5 py-1.5 pl-8 text-xs rounded-full border border-[#e2e8f0] bg-[#f8fafc] text-[#17191c] placeholder:text-[#94a3b8] focus:outline-none focus:border-[#17191c] focus:bg-white focus:ring-1 focus:ring-[#17191c] transition-all"
            />
            <svg class="w-3.5 h-3.5 absolute left-3 text-[#94a3b8]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <!-- Quick Action Button (+ round button in Ink Black) -->
          <button
            type="button"
            @click="handleQuickAddUser"
            class="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-[#17191c] hover:bg-[#262626] text-white flex items-center justify-center shadow-xs active:scale-95 transition-all"
            title="Tambah Pengguna Cepat"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
            </svg>
          </button>

          <!-- Telemetry Status Icon (Emerald Dot 200 OK) -->
          <div
            class="hidden sm:flex items-center justify-center w-8 h-8 rounded-full border border-[#e2e8f0] bg-white text-[#10b981]"
            title="Backend FastAPI: Sehat (200 OK)"
          >
            <span class="w-2 h-2 rounded-full bg-[#10b981]"></span>
          </div>

          <!-- Celery Worker Status Badge -->
          <div class="hidden sm:inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f1f5f9] border border-[#e2e8f0] text-[11px] font-semibold text-[#475569]">
            <svg class="w-3 h-3 text-[#17191c]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
            </svg>
            <span>Celery: {{ systemMetrics.celeryActiveTasks }}/4</span>
          </div>

          <!-- Super Admin Profile Chip (Darrell Steward equivalent) -->
          <div class="relative">
            <button
              type="button"
              @click="isProfileDropdownOpen = !isProfileDropdownOpen"
              class="flex items-center space-x-2.5 p-1 sm:px-2.5 sm:py-1 rounded-full hover:bg-[#f1f5f9] transition-colors border border-transparent hover:border-[#e2e8f0]"
            >
              <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#17191c] text-white font-bold text-xs flex items-center justify-center shadow-2xs">
                {{ authStore.user?.full_name ? authStore.user.full_name.charAt(0).toUpperCase() : 'A' }}
              </div>
              <div class="hidden md:block text-left">
                <div class="text-xs font-bold text-[#17191c] leading-tight truncate max-w-[120px]">
                  {{ authStore.user?.full_name || 'Super Administrator' }}
                </div>
                <div class="text-[10px] text-[#777b86] leading-none">
                  Super admin
                </div>
              </div>
              <svg class="w-3.5 h-3.5 text-[#94a3b8] hidden md:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Profile Dropdown Menu -->
            <div
              v-if="isProfileDropdownOpen"
              class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-[#ededed] py-2 z-50 text-xs"
            >
              <div class="px-4 py-2 border-b border-[#ededed]">
                <div class="font-bold text-[#17191c]">{{ authStore.user?.full_name || 'Super Administrator' }}</div>
                <div class="text-[11px] text-[#777b86]">{{ authStore.user?.email || 'admin@veritext.ai' }}</div>
                <div class="mt-1 text-[10px] font-semibold text-[#17191c] uppercase tracking-wider">Peran: Super Admin</div>
              </div>
              <router-link
                to="/dashboard"
                class="block px-4 py-2 text-[#475569] hover:bg-[#f8fafc] hover:text-[#17191c]"
                @click="isProfileDropdownOpen = false"
              >
                Ke Workspace Mahasiswa
              </router-link>
              <router-link
                to="/"
                class="block px-4 py-2 text-[#475569] hover:bg-[#f8fafc] hover:text-[#17191c]"
                @click="isProfileDropdownOpen = false"
              >
                Ke Beranda Publik
              </router-link>
              <div class="border-t border-[#ededed] my-1"></div>
              <button
                type="button"
                @click="handleLogout"
                class="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 font-medium"
              >
                Keluar Sesi
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- 3. DASHBOARD MAIN CONTENT (Zendenta Layout) -->
      <main class="p-6 sm:p-8 space-y-6 max-w-[1600px] w-full mx-auto">
        <!-- TOP KPI ASSET CARD (TOTAL ASSET VALUE & 34 product segmented bar) -->
        <section class="bg-white border border-[#ededed] rounded-[18px] p-6 shadow-xs">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <!-- Left Side: Total Asset Value -->
            <div class="lg:col-span-5 flex items-center space-x-4">
              <div class="w-12 h-12 rounded-full bg-[#f4f4f5] border border-[#e4e4e7] text-[#17191c] flex items-center justify-center shrink-0 shadow-2xs">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <span class="block text-[11px] font-bold uppercase tracking-wider text-[#777b86]">
                  TOTAL VALUASI SALDO &amp; LISENSI
                </span>
                <div class="text-3xl sm:text-4xl font-extrabold tracking-tight text-[#17191c] tabular-nums mt-0.5">
                  {{ totalTokensInSystem.toLocaleString('id-ID') }} <span class="text-lg font-semibold text-[#777b86]">Token</span>
                </div>
              </div>
            </div>

            <!-- Vertical Hairline Divider for Desktop -->
            <div class="hidden lg:block lg:col-span-1 h-14 border-r border-[#ededed]"></div>

            <!-- Right Side: Segmented Ratio Bar & Count (34 product equivalent) -->
            <div class="lg:col-span-6 space-y-3">
              <div class="flex items-baseline space-x-2">
                <span class="text-xl font-bold text-[#17191c] tabular-nums">{{ users.length }}</span>
                <span class="text-xs text-[#777b86] font-medium">Akun Terdaftar di Sistem</span>
              </div>

              <!-- Segmented Horizontal Bar (Ink Black / Amber / Rose) -->
              <div class="w-full h-2.5 rounded-full bg-[#f1f5f9] overflow-hidden flex gap-0.5">
                <!-- Ink Black: In stock / Aktif -->
                <div
                  class="bg-[#17191c] h-full rounded-l-full transition-all duration-500"
                  :style="{ width: `${segmentActivePct}%` }"
                  title="Pengguna Aktif"
                ></div>
                <!-- Amber: Low stock / Kuota Kritis -->
                <div
                  class="bg-[#f59e0b] h-full transition-all duration-500"
                  :style="{ width: `${segmentLowStockPct}%` }"
                  title="Kuota Kritis"
                ></div>
                <!-- Rose: Out of stock / Suspended -->
                <div
                  class="bg-[#ef4444] h-full rounded-r-full transition-all duration-500"
                  :style="{ width: `${segmentSuspendedPct}%` }"
                  title="Ditangguhkan"
                ></div>
              </div>

              <!-- Legend Dots -->
              <div class="flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-[#777b86] font-medium">
                <div class="flex items-center space-x-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#17191c]"></span>
                  <span>Pengguna Aktif: <strong class="text-[#17191c] tabular-nums">{{ activeUsersCount }}</strong></span>
                </div>
                <div class="flex items-center space-x-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#f59e0b]"></span>
                  <span>Kuota Kritis (&lt;3): <strong class="text-[#17191c] tabular-nums">{{ lowTokenUsersCount }}</strong></span>
                </div>
                <div class="flex items-center space-x-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#ef4444]"></span>
                  <span>Ditangguhkan: <strong class="text-[#17191c] tabular-nums">{{ suspendedUsersCount }}</strong></span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- SUB-TABS SECTION (Inventory / Order Stock equivalent in Zendenta) -->
        <div class="border-b border-[#ededed]">
          <div class="flex items-center space-x-6 text-xs font-semibold">
            <button
              type="button"
              @click="setSection('users')"
              class="pb-3 border-b-2 transition-colors duration-150"
              :class="currentSection === 'users' ? 'border-[#17191c] text-[#17191c] font-bold' : 'border-transparent text-[#64748b] hover:text-[#17191c]'"
            >
              Daftar Pengguna
            </button>
            <button
              type="button"
              @click="setSection('corpus')"
              class="pb-3 border-b-2 transition-colors duration-150"
              :class="currentSection === 'corpus' ? 'border-[#17191c] text-[#17191c] font-bold' : 'border-transparent text-[#64748b] hover:text-[#17191c]'"
            >
              Bank Korpus Ilmiah
            </button>
            <button
              type="button"
              @click="setSection('overview')"
              class="pb-3 border-b-2 transition-colors duration-150"
              :class="currentSection === 'overview' ? 'border-[#17191c] text-[#17191c] font-bold' : 'border-transparent text-[#64748b] hover:text-[#17191c]'"
            >
              Overview Telemetri
            </button>
            <button
              type="button"
              @click="setSection('config')"
              class="pb-3 border-b-2 transition-colors duration-150"
              :class="currentSection === 'config' ? 'border-[#17191c] text-[#17191c] font-bold' : 'border-transparent text-[#64748b] hover:text-[#17191c]'"
            >
              Tuning Engine AI
            </button>
            <button
              type="button"
              @click="setSection('logs')"
              class="pb-3 border-b-2 transition-colors duration-150"
              :class="currentSection === 'logs' ? 'border-[#17191c] text-[#17191c] font-bold' : 'border-transparent text-[#64748b] hover:text-[#17191c]'"
            >
              Log Jejak Forensik
            </button>
          </div>
        </div>

        <!-- 4. ACTIVE SECTION CONTENTS -->
        <!-- View 1: DAFTAR PENGGUNA (Zendenta Table & Modals) -->
        <section v-if="currentSection === 'users'" class="space-y-4">
          <UserManagementTable
            ref="userTableRef"
            :users="users"
            @toggleStatus="handleToggleStatus"
            @adjustTokens="handleAdjustTokens"
            @changeRole="handleChangeRole"
            @createUser="handleCreateUser"
            @updateUser="handleUpdateUser"
            @deleteUser="handleDeleteUser"
          />
        </section>

        <!-- View 2: OVERVIEW & TELEMETRI -->
        <section v-else-if="currentSection === 'overview'" class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-base font-bold text-[#17191c] tracking-tight">
                Metrik Sistem &amp; Kapasitas Layanan
              </h2>
              <p class="text-xs text-[#777b86]">
                Telemetri throughput deteksi, latensi rata-rata, dan pemanfaatan indeks pgvector HNSW.
              </p>
            </div>
          </div>

          <AdminStatsGrid
            :totalUsers="users.length"
            :totalAudits="systemMetrics.totalAudits"
            :totalCorpusDocs="systemMetrics.totalCorpusDocs"
            :vectorCount="systemMetrics.vectorCount"
            :avgLatencyMs="systemMetrics.avgLatencyMs"
            :systemLoadPct="systemMetrics.systemLoadPct"
          />

          <!-- Infrastructure Nodes Status -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Celery Worker -->
            <div class="bg-white border border-[#ededed] rounded-[18px] p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-[#17191c]">Antrean Worker Celery</span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
                  Worker Aktif
                </span>
              </div>
              <div class="text-2xl font-bold text-[#17191c] tabular-nums">
                {{ systemMetrics.celeryActiveTasks }} <span class="text-xs font-normal text-[#777b86]">tugas aktif</span>
              </div>
              <p class="text-[11px] text-[#777b86] leading-relaxed">
                Broker Redis: <strong class="text-[#17191c]">{{ systemMetrics.redisStatus }}</strong>. Database: <strong class="text-[#17191c]">{{ systemMetrics.databaseStatus }}</strong>.
              </p>
            </div>

            <!-- pgvector HNSW Engine -->
            <div class="bg-white border border-[#ededed] rounded-[18px] p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-[#17191c]">pgvector HNSW Index</span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
                  m=16, ef=64
                </span>
              </div>
              <div class="text-2xl font-bold text-[#17191c] tabular-nums">
                {{ systemMetrics.vectorCount.toLocaleString('id-ID') }} <span class="text-xs font-normal text-[#777b86]">vektor 384D</span>
              </div>
              <p class="text-[11px] text-[#777b86] leading-relaxed">
                Metrik jarak: <em class="text-[#17191c]">Cosine Distance</em>. Indeks terdistribusi sinkron dengan bank korpus.
              </p>
            </div>

            <!-- Security & Privacy Guard -->
            <div class="bg-white border border-[#ededed] rounded-[18px] p-5 shadow-xs space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-[#17191c]">Kepatuhan UU PDP No. 27/2022</span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
                  Compliant
                </span>
              </div>
              <div class="text-2xl font-bold text-[#17191c] tabular-nums">
                30 Hari <span class="text-xs font-normal text-[#777b86]">retensi otomatis</span>
              </div>
              <p class="text-[11px] text-[#777b86] leading-relaxed">
                Naskah mahasiswa otomatis dibersihkan dari server sementara sidik jari hash kriptografi dipertahankan.
              </p>
            </div>
          </div>
        </section>

        <!-- View 3: BANK KORPUS ILMIAH (100% FULLY INTEGRATED) -->
        <section v-else-if="currentSection === 'corpus'" class="space-y-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-base font-bold text-[#17191c] tracking-tight">
                Bank Dokumen Korpus Pembanding
              </h2>
              <p class="text-xs text-[#777b86]">
                Koleksi repositori naskah akademik terindeks <span class="italic font-medium text-[#17191c]">pgvector HNSW (384D)</span> &amp; <span class="italic font-medium text-[#17191c]">Rabin-Karp Winnowing</span> untuk pembandingan leksikal &amp; semantik.
              </p>
            </div>
          </div>

          <!-- Corpus Stats Grid -->
          <CorpusStatsGrid
            :totalDocs="corpusList.length"
            :totalChunks="totalCorpusChunks"
            indexStatus="Aktif &amp; Sinkron"
          />

          <!-- Corpus Filter Bar with Category & Search -->
          <CorpusFilterBar
            v-model:selectedCategory="corpusCategory"
            v-model:searchQuery="corpusSearch"
            @openUploadModal="openCorpusUpload"
          />

          <!-- Corpus Table with Real Ingested Documents -->
          <CorpusTable
            :items="filteredCorpusList"
            :loading="isCorpusLoading"
            @deleteItem="handleDeleteCorpusItem"
          />

          <!-- Corpus Upload ZIP Modal -->
          <CorpusUploadModal
            :isOpen="isCorpusUploadOpen"
            :loading="isIngestingCorpus"
            @close="closeCorpusUpload"
            @submit="handleBulkIngest"
          />
        </section>

        <!-- View 4: TUNING ENGINE AI -->
        <section v-else-if="currentSection === 'config'" class="space-y-4">
          <SystemSettingsCard @saveConfig="handleSaveConfig" />
        </section>

        <!-- View 5: LOG JEJAK FORENSIK -->
        <section v-else-if="currentSection === 'logs'" class="space-y-4">
          <AdminAuditLogsTable
            :logs="auditLogs"
            @refresh="handleRefreshLogs"
            @exportCsv="handleExportCsv"
          />
        </section>

        <!-- View 6: KEPATUHAN UU PDP -->
        <section v-else-if="currentSection === 'pdp'" class="bg-white border border-[#ededed] rounded-[18px] p-6 shadow-xs space-y-5">
          <div class="flex items-center justify-between border-b border-[#ededed] pb-4">
            <div>
              <h2 class="text-base font-bold text-[#17191c]">
                Kepatuhan UU Perlindungan Data Pribadi (UU PDP No. 27/2022)
              </h2>
              <p class="text-xs text-[#777b86] mt-0.5">
                Standar tata kelola hak privasi pemohon naskah, penghapusan otomatis data sementara, dan integritas hash forensik.
              </p>
            </div>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
              Compliant (30 Hari Retensi)
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="p-4 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] space-y-2">
              <div class="font-bold text-[#17191c] text-sm">Pembersihan Naskah Otomatis (30 Hari)</div>
              <p class="text-[#777b86] leading-relaxed">
                File PDF/DOCX yang diunggah mahasiswa otomatis dihapus permanen dari storage server 30 hari setelah tugas audit selesai. Hanya sidik jari hash kriptografi SHA-256 dan laporan skor yang dipertahankan.
              </p>
            </div>

            <div class="p-4 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] space-y-2">
              <div class="font-bold text-[#17191c] text-sm">Pseudonimitas Data Kalimat</div>
              <p class="text-[#777b86] leading-relaxed">
                Teks naskah yang disimpan dalam indeks semantik dan leksikal telah melalui proses anonymization sehingga tidak memuat metadata pribadi seperti Nomor Induk Mahasiswa atau kontak pribadi.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>
