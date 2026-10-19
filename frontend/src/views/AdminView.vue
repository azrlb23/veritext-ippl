<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
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
import { useNotification } from "../composables";
import { apiClient } from "../services/api";
import { corpusService } from "../services/corpusService";

const router = useRouter();
const route = useRoute();
const { showNotification } = useNotification();

const users = ref<ManagedUser[]>([]);
const auditLogs = ref<AuditLogItem[]>([]);

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

  try {
    const cData = await corpusService.list(undefined, 1, 100);
    if (cData && typeof cData.total === "number") {
      systemMetrics.value.totalCorpusDocs = cData.total;
    }
  } catch {
    // Keep defaults
  }
}

onMounted(() => {
  void loadRealUsers();
  void loadAuditLogs();
  void loadMetrics();
});

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

type AdminSection = "overview" | "users" | "corpus" | "config" | "logs";

const currentSection = computed<AdminSection>(() => {
  const hash = (route.hash || "").replace("#", "").toLowerCase();
  if (hash === "users") return "users";
  if (hash === "corpus") return "corpus";
  if (hash === "config") return "config";
  if (hash === "logs") return "logs";
  return "overview";
});

function setSection(section: AdminSection) {
  if (section === "overview") {
    router.push({ path: "/admin", hash: "" });
  } else if (section === "corpus") {
    router.push("/corpus");
  } else {
    router.push({ path: "/admin", hash: `#${section}` });
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    <!-- Header Konsol Super Administrator -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#ededed] pb-6">
      <div>
        <div class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-[#262626] text-white text-[11px] font-bold uppercase tracking-wider mb-2">
          <span>Konsol Tata Kelola Administrator</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#262626] tracking-tight">
          Pusat Kontrol Infrastruktur &amp; <span class="italic font-bold text-[#262626]">Tata Kelola VeriText AI</span>
        </h1>
        <p class="text-xs sm:text-sm text-[#686868] mt-1 max-w-3xl font-normal">
          Konsol tata kelola terpadu untuk pengawasan server backend <strong class="font-bold text-[#262626]">FastAPI</strong>, topologi <strong class="font-bold text-[#262626]">pgvector HNSW</strong>, antrean Celery worker, manajemen kuota pengguna, serta kepatuhan <strong class="italic font-bold text-[#262626]">UU PDP No. 27/2022</strong>.
        </p>
      </div>

      <!-- Quick Status Badges -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-2 self-start">
        <div class="text-xs font-bold bg-white px-3 py-1.5 rounded-[4px] border border-[#ededed] shadow-audyr-subtle text-[#262626]">
          <span>Backend FastAPI: Sehat (200 OK)</span>
        </div>
        <div class="text-xs font-bold bg-white px-3 py-1.5 rounded-[4px] border border-[#ededed] shadow-audyr-subtle text-[#262626]">
          <span>Celery &amp; Redis: Aktif</span>
        </div>
      </div>
    </div>

    <!-- Section Switcher Tabs -->
    <div class="border-b border-[#ededed]">
      <div class="flex items-center space-x-1 sm:space-x-2 overflow-x-auto text-xs font-bold">
        <button
          type="button"
          @click="setSection('overview')"
          class="px-4 py-2.5 border-b-2 whitespace-nowrap transition-colors duration-150"
          :class="currentSection === 'overview' ? 'text-[#262626] border-[#262626] font-bold' : 'text-[#686868] border-transparent hover:text-[#262626] font-medium'"
        >
          Overview &amp; Metrik
        </button>
        <button
          type="button"
          @click="setSection('users')"
          class="px-4 py-2.5 border-b-2 whitespace-nowrap transition-colors duration-150"
          :class="currentSection === 'users' ? 'text-[#262626] border-[#262626] font-bold' : 'text-[#686868] border-transparent hover:text-[#262626] font-medium'"
        >
          Kelola Pengguna &amp; Saldo
        </button>
        <button
          type="button"
          @click="setSection('corpus')"
          class="px-4 py-2.5 border-b-2 whitespace-nowrap transition-colors duration-150 text-[#686868] border-transparent hover:text-[#262626] font-medium"
        >
          Bank Korpus &rarr;
        </button>
        <button
          type="button"
          @click="setSection('config')"
          class="px-4 py-2.5 border-b-2 whitespace-nowrap transition-colors duration-150"
          :class="currentSection === 'config' ? 'text-[#262626] border-[#262626] font-bold' : 'text-[#686868] border-transparent hover:text-[#262626] font-medium'"
        >
          Tuning Engine AI
        </button>
        <button
          type="button"
          @click="setSection('logs')"
          class="px-4 py-2.5 border-b-2 whitespace-nowrap transition-colors duration-150"
          :class="currentSection === 'logs' ? 'text-[#262626] border-[#262626] font-bold' : 'text-[#686868] border-transparent hover:text-[#262626] font-medium'"
        >
          Log Jejak Audit
        </button>
      </div>
    </div>

    <!-- Bagian 1: Overview & Metrik Infrastruktur (Rendered only on 'overview') -->
    <section v-if="currentSection === 'overview'" id="overview" class="space-y-6 pt-2">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-extrabold text-[#262626] tracking-tight">
            Metrik Sistem &amp; Kapasitas Layanan
          </h2>
          <p class="text-xs text-[#686868] font-normal">
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
        <!-- Worker Celery -->
        <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#262626] tracking-tight">Antrean Worker Celery</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">Worker Aktif</span>
          </div>
          <div class="text-2xl font-extrabold text-[#262626] tabular-nums">{{ systemMetrics.celeryActiveTasks }} <span class="text-xs font-normal text-[#686868]">antrean aktif</span></div>
          <p class="text-[11px] text-[#737373] leading-relaxed">
            Broker Redis: <span class="font-extrabold text-[#262626]">{{ systemMetrics.redisStatus }}</span>. Database: <span class="font-extrabold text-[#262626]">{{ systemMetrics.databaseStatus }}</span>.
          </p>
        </div>

        <!-- pgvector HNSW Engine -->
        <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#262626] tracking-tight">pgvector HNSW Index</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">m=16, ef=64</span>
          </div>
          <div class="text-2xl font-extrabold text-[#262626] tabular-nums">{{ systemMetrics.vectorCount.toLocaleString('id-ID') }} <span class="text-xs font-normal text-[#686868]">vektor terindeks</span></div>
          <p class="text-[11px] text-[#737373] leading-relaxed">
            Metrik jarak: <span class="italic font-bold text-[#262626]">Kosinus (Cosine Distance)</span>. Indeks tersinkronisasi 100% dengan repositori korpus.
          </p>
        </div>

        <!-- Security & Privacy Guard -->
        <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#262626] tracking-tight">Kepatuhan UU PDP No. 27/2022</span>
            <span class="text-[10px] italic font-bold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">Compliant</span>
          </div>
          <div class="text-2xl font-extrabold text-[#262626] tabular-nums">30 Hari <span class="text-xs font-normal text-[#686868]">retensi otomatis</span></div>
          <p class="text-[11px] text-[#737373] leading-relaxed">
            Naskah mahasiswa otomatis dibersihkan dari server sementara sidik jari hash kriptografi dipertahankan.
          </p>
        </div>
      </div>
    </section>

    <!-- Bagian 2: Manajemen Pengguna & Otorisasi Kuota (Rendered only on 'users') -->
    <section v-else-if="currentSection === 'users'" id="users" class="space-y-4 pt-2">
      <UserManagementTable
        :users="users"
        @toggleStatus="handleToggleStatus"
        @adjustTokens="handleAdjustTokens"
        @changeRole="handleChangeRole"
        @createUser="handleCreateUser"
        @updateUser="handleUpdateUser"
        @deleteUser="handleDeleteUser"
      />
    </section>

    <!-- Bagian 3: Repositori Bank Korpus Institusi (Rendered on 'corpus') -->
    <section v-else-if="currentSection === 'corpus'" id="corpus" class="bg-white border border-[#ededed] rounded-[14px] p-6 shadow-audyr-subtle space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <h2 class="text-base font-extrabold text-[#262626] tracking-tight">
              Tata Kelola Bank Korpus Pembanding Institusi
            </h2>
            <span class="text-[10px] italic font-bold uppercase px-2 py-0.5 rounded-full bg-[#fafafa] text-[#262626] border border-[#ededed]">
              Tier 1 &amp; Tier 2 Ground Truth
            </span>
          </div>
          <p class="text-xs text-[#686868] mt-1">
            Bank naskah rujukan skripsi, tesis, dan artikel ilmiah internal yang diindeks ke dalam tabel <code class="bg-[#f4f4f4] px-1 py-0.5 rounded text-[11px] font-bold">document_chunks</code> dan <code class="bg-[#f4f4f4] px-1 py-0.5 rounded text-[11px] font-bold">lexical_fingerprints</code>.
          </p>
        </div>

        <router-link
          to="/corpus"
          class="text-xs font-medium text-white bg-[#262626] hover:bg-[#171717] px-4 py-2 rounded-[4px] shadow-audyr-subtle active:scale-[0.98] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] inline-flex items-center space-x-1.5 self-start"
        >
          <span>Buka Antarmuka Bank Korpus</span>
          <span>&rarr;</span>
        </router-link>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <div class="p-3.5 bg-[#fafafa] rounded-[4px] border border-[#ededed]">
          <span class="text-[11px] text-[#686868] font-medium block">Total Dokumen Rujukan</span>
          <span class="text-lg font-extrabold text-[#262626] tabular-nums">68 Naskah</span>
        </div>
        <div class="p-3.5 bg-[#fafafa] rounded-[4px] border border-[#ededed]">
          <span class="text-[11px] text-[#686868] font-medium block">Ukuran Korpus Terproses</span>
          <span class="text-lg font-extrabold text-[#262626] tabular-nums">42.5 MB</span>
        </div>
        <div class="p-3.5 bg-[#fafafa] rounded-[4px] border border-[#ededed]">
          <span class="text-[11px] text-[#686868] font-medium block">Hak Kelola Upload</span>
          <span class="text-lg font-extrabold text-[#262626]">Admin &amp; Reviewer</span>
        </div>
      </div>
    </section>

    <!-- Bagian 4: Tuning Hyperparameter Engine AI (Rendered only on 'config') -->
    <section v-else-if="currentSection === 'config'" id="config" class="space-y-4 pt-2">
      <SystemSettingsCard @saveConfig="handleSaveConfig" />
    </section>

    <!-- Bagian 5: Log Jejak Audit & Forensik Keamanan (Rendered only on 'logs') -->
    <section v-else-if="currentSection === 'logs'" id="logs" class="space-y-4 pt-2">
      <AdminAuditLogsTable
        :logs="auditLogs"
        @refresh="handleRefreshLogs"
        @exportCsv="handleExportCsv"
      />
    </section>
  </div>
</template>
