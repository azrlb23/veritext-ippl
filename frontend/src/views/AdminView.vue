<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
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

const route = useRoute();
const { showNotification } = useNotification();

const users = ref<ManagedUser[]>([
  {
    id: "usr-001",
    full_name: "Dr. Budi Santoso",
    email: "budi.santoso@ui.ac.id",
    institution: "Universitas Indonesia",
    role: "ADMIN",
    token_balance: 50,
    is_active: true,
    created_at: "2026-08-12",
  },
  {
    id: "usr-002",
    full_name: "Prof. Siti Aminah, M.Kom",
    email: "siti.aminah@itb.ac.id",
    institution: "Institut Teknologi Bandung",
    role: "REVIEWER",
    token_balance: 35,
    is_active: true,
    created_at: "2026-09-01",
  },
  {
    id: "usr-003",
    full_name: "Ahmad Dahlan",
    email: "ahmad.d@ugm.ac.id",
    institution: "Universitas Gadjah Mada",
    role: "PREMIUM",
    token_balance: 15,
    is_active: true,
    created_at: "2026-09-18",
  },
  {
    id: "usr-004",
    full_name: "Rina Kusuma",
    email: "rina.k@student.ui.ac.id",
    institution: "Universitas Indonesia",
    role: "TRIAL",
    token_balance: 5,
    is_active: true,
    created_at: "2026-10-05",
  },
  {
    id: "usr-005",
    full_name: "Mochammad Azriel Albian Putra",
    email: "azriel@kampus.ac.id",
    institution: "Institut Teknologi Nasional",
    role: "TRIAL",
    token_balance: 5,
    is_active: true,
    created_at: "2026-10-18",
  },
]);

const auditLogs = ref<AuditLogItem[]>([
  {
    id: "log-101",
    timestamp: "2026-10-18 21:42:15",
    actor_name: "Super Administrator",
    actor_email: "admin@veritext.ai",
    action: "TOKEN_ADJUST",
    target_resource: "usr-002 (Prof. Siti Aminah)",
    ip_address: "192.168.1.10",
    status: "SUCCESS",
    details: "Koreksi saldo kuota +20 token untuk pengujian semester ganjil.",
  },
  {
    id: "log-102",
    timestamp: "2026-10-18 20:15:02",
    actor_name: "Super Administrator",
    actor_email: "admin@veritext.ai",
    action: "CONFIG_UPDATE",
    target_resource: "engine_hyperparameters",
    ip_address: "192.168.1.10",
    status: "SUCCESS",
    details: "Tuning ambang batas kosinus HNSW menjadi 0.82 dan winnowing k-gram=5.",
  },
  {
    id: "log-103",
    timestamp: "2026-10-18 18:30:45",
    actor_name: "Prof. Siti Aminah, M.Kom",
    actor_email: "siti.aminah@itb.ac.id",
    action: "CORPUS_INGEST",
    target_resource: "korpus_skripsi_itb_2025.zip",
    ip_address: "10.20.4.88",
    status: "SUCCESS",
    details: "Ingestion bulk 14 berkas korpus rujukan internal kampus.",
  },
  {
    id: "log-104",
    timestamp: "2026-10-18 16:10:19",
    actor_name: "Super Administrator",
    actor_email: "admin@veritext.ai",
    action: "USER_SUSPEND",
    target_resource: "usr-099 (Spam Account)",
    ip_address: "192.168.1.10",
    status: "SUCCESS",
    details: "Suspensi akun terindikasi automated scraping payload.",
  },
  {
    id: "log-105",
    timestamp: "2026-10-18 14:02:30",
    actor_name: "Sistem Otomatis UU PDP",
    actor_email: "daemon@veritext.ai",
    action: "DOCUMENT_PURGE",
    target_resource: "doc-temp-expired-hash-8f4b",
    ip_address: "127.0.0.1",
    status: "SUCCESS",
    details: "Pembersihan berkas naskah kedaluwarsa setelah 30 hari sesuai UU PDP No. 27/2022.",
  },
]);

function handleToggleStatus(userId: string) {
  const user = users.value.find((u) => u.id === userId);
  if (user) {
    user.is_active = !user.is_active;
    const actionType = user.is_active ? "USER_ACTIVATE" : "USER_SUSPEND";

    // Catat ke log audit
    auditLogs.value.unshift({
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      actor_name: "Super Administrator",
      actor_email: "admin@veritext.ai",
      action: actionType,
      target_resource: `${user.id} (${user.full_name})`,
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      details: `Status akun diubah menjadi ${user.is_active ? "Aktif" : "Nonaktif"}.`,
    });

    showNotification(
      `Status pengguna ${user.full_name} berhasil diubah menjadi ${user.is_active ? "Aktif" : "Nonaktif"}.`,
      "info",
      "Perubahan Status"
    );
  }
}

function handleAdjustTokens(userId: string, delta: number) {
  const user = users.value.find((u) => u.id === userId);
  if (user) {
    user.token_balance = Math.max(0, user.token_balance + delta);

    // Catat ke log audit
    auditLogs.value.unshift({
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      actor_name: "Super Administrator",
      actor_email: "admin@veritext.ai",
      action: "TOKEN_ADJUST",
      target_resource: `${user.id} (${user.full_name})`,
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      details: `Penyesuaian kuota token sebesar ${delta > 0 ? "+" + delta : delta}. Total baru: ${user.token_balance}`,
    });

    showNotification(
      `Berhasil memperbarui ${delta > 0 ? "+" + delta : delta} token untuk ${user.full_name}. Saldo kini: ${user.token_balance}`,
      "success",
      "Penyesuaian Token"
    );
  }
}

function handleChangeRole(userId: string, newRole: ManagedUser["role"]) {
  const user = users.value.find((u) => u.id === userId);
  if (user) {
    const oldRole = user.role;
    user.role = newRole;

    auditLogs.value.unshift({
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      actor_name: "Super Administrator",
      actor_email: "admin@veritext.ai",
      action: "ROLE_CHANGE",
      target_resource: `${user.id} (${user.full_name})`,
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      details: `Peran diubah dari ${oldRole} menjadi ${newRole}.`,
    });

    showNotification(
      `Peran pengguna ${user.full_name} diubah menjadi ${newRole}.`,
      "info"
    );
  }
}

function handleSaveConfig(newConfig: SystemConfig) {
  auditLogs.value.unshift({
    id: `log-${Date.now()}`,
    timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
    actor_name: "Super Administrator",
    actor_email: "admin@veritext.ai",
    action: "CONFIG_UPDATE",
    target_resource: "engine_hyperparameters",
    ip_address: "127.0.0.1",
    status: "SUCCESS",
    details: `Tuning parameter: Ambang kosinus=${newConfig.hnsw_similarity_threshold}, k-gram=${newConfig.winnowing_kgram}, window=${newConfig.winnowing_window}`,
  });

  showNotification(
    `Hyperparameter sistem berhasil diperbarui. Ambang batas kosinus: ${newConfig.hnsw_similarity_threshold}`,
    "success",
    "Konfigurasi Tersimpan"
  );
}

function handleRefreshLogs() {
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

onMounted(() => {
  if (route.hash) {
    const el = document.querySelector(route.hash);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  }
});
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Header Konsol Super Administrator -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#ededed] pb-6">
      <div>
        <div class="inline-flex items-center space-x-2 px-3 py-0.5 rounded-full bg-[#262626] text-white text-xs font-bold uppercase tracking-wider mb-2">
          <span>🛡️</span>
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
        <div class="flex items-center space-x-2 text-xs font-bold bg-white px-3 py-1.5 rounded-[4px] border border-[#ededed] shadow-audyr-subtle text-[#262626]">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Backend FastAPI: Sehat (200 OK)</span>
        </div>
        <div class="flex items-center space-x-2 text-xs font-bold bg-white px-3 py-1.5 rounded-[4px] border border-[#ededed] shadow-audyr-subtle text-[#262626]">
          <span class="w-2 h-2 rounded-full bg-[#059669]"></span>
          <span>Celery &amp; Redis: Aktif</span>
        </div>
      </div>
    </div>

    <!-- Quick Navigation Anchor Subnav -->
    <div class="flex items-center space-x-2 overflow-x-auto pb-1 text-xs font-bold text-[#686868]">
      <a
        href="#overview"
        class="px-3 py-1.5 rounded-[4px] border border-[#ededed] bg-white hover:bg-[#fafafa] hover:text-[#262626] whitespace-nowrap transition-colors duration-150"
      >
        📊 Overview &amp; Metrik
      </a>
      <a
        href="#users"
        class="px-3 py-1.5 rounded-[4px] border border-[#ededed] bg-white hover:bg-[#fafafa] hover:text-[#262626] whitespace-nowrap transition-colors duration-150"
      >
        👥 Kelola Pengguna &amp; Saldo
      </a>
      <a
        href="#corpus"
        class="px-3 py-1.5 rounded-[4px] border border-[#ededed] bg-white hover:bg-[#fafafa] hover:text-[#262626] whitespace-nowrap transition-colors duration-150"
      >
        📚 Repositori Korpus
      </a>
      <a
        href="#config"
        class="px-3 py-1.5 rounded-[4px] border border-[#ededed] bg-white hover:bg-[#fafafa] hover:text-[#262626] whitespace-nowrap transition-colors duration-150"
      >
        ⚙️ Tuning Engine AI
      </a>
      <a
        href="#logs"
        class="px-3 py-1.5 rounded-[4px] border border-[#ededed] bg-white hover:bg-[#fafafa] hover:text-[#262626] whitespace-nowrap transition-colors duration-150"
      >
        📜 Log Jejak Audit
      </a>
    </div>

    <!-- Bagian 1: Overview & Metrik Infrastruktur -->
    <section id="overview" class="space-y-4 pt-2">
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
        :totalAudits="842"
        :totalCorpusDocs="68"
        :vectorCount="24500"
        :avgLatencyMs="118"
        :systemLoadPct="28"
      />

      <!-- Infrastructure Nodes Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Worker Celery -->
        <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#262626] tracking-tight">Antrean Worker Celery</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">4 Worker Aktif</span>
          </div>
          <div class="text-2xl font-extrabold text-[#262626] tabular-nums">0 <span class="text-xs font-normal text-[#686868]">antrean tertunda</span></div>
          <p class="text-[11px] text-[#737373] leading-relaxed">
            Broker Redis berjalan di port 6379. Rata-rata waktu konsumsi tugas audit hybrid: <span class="font-extrabold text-[#262626]">1.4 detik</span>.
          </p>
        </div>

        <!-- pgvector HNSW Engine -->
        <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#262626] tracking-tight">pgvector HNSW Index</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">m=16, ef=64</span>
          </div>
          <div class="text-2xl font-extrabold text-[#262626] tabular-nums">24,500 <span class="text-xs font-normal text-[#686868]">vektor terindeks</span></div>
          <p class="text-[11px] text-[#737373] leading-relaxed">
            Metrik jarak: <span class="italic font-bold text-[#262626]">Kosinus (Cosine Distance)</span>. Indeks tersinkronisasi 100% dengan tabel korpus.
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

    <!-- Bagian 2: Manajemen Pengguna & Otorisasi Kuota -->
    <section id="users" class="space-y-4 pt-4">
      <UserManagementTable
        :users="users"
        @toggleStatus="handleToggleStatus"
        @adjustTokens="handleAdjustTokens"
        @changeRole="handleChangeRole"
      />
    </section>

    <!-- Bagian 3: Repositori Bank Korpus Institusi -->
    <section id="corpus" class="bg-white border border-[#ededed] rounded-[14px] p-6 shadow-audyr-subtle space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <h2 class="text-base font-extrabold text-[#262626] tracking-tight">
              Tata Kelola Bank Korpus Pembanding Institusi
            </h2>
            <span class="text-[10px] italic font-bold uppercase px-2 py-0.5 rounded-full bg-[#fafafa] text-[#262626] border border-[#ededed]">
              Tier 1 & Tier 2 Ground Truth
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
          <span class="text-lg font-extrabold text-[#262626]">Admin & Reviewer</span>
        </div>
      </div>
    </section>

    <!-- Bagian 4: Tuning Hyperparameter Engine AI -->
    <section id="config" class="space-y-4 pt-4">
      <SystemSettingsCard @saveConfig="handleSaveConfig" />
    </section>

    <!-- Bagian 5: Log Jejak Audit & Forensik Keamanan -->
    <section id="logs" class="space-y-4 pt-4">
      <AdminAuditLogsTable
        :logs="auditLogs"
        @refresh="handleRefreshLogs"
        @exportCsv="handleExportCsv"
      />
    </section>
  </div>
</template>
