<script setup lang="ts">
import { ref, computed } from "vue";
import Badge from "../common/Badge.vue";
import EmptyState from "../common/EmptyState.vue";
import SkeletonLoader from "../common/SkeletonLoader.vue";
import type { AuditLogItem } from "../../types/admin";

interface Props {
  logs: AuditLogItem[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "refresh"): void;
  (e: "exportCsv"): void;
}>();

const searchQuery = ref("");
const statusFilter = ref<string>("ALL");
const actionFilter = ref<string>("ALL");

const filteredLogs = computed(() => {
  return props.logs.filter((log) => {
    const matchesStatus = statusFilter.value === "ALL" || log.status === statusFilter.value;
    const matchesAction = actionFilter.value === "ALL" || log.action === actionFilter.value;
    const q = searchQuery.value.toLowerCase().trim();
    const matchesQuery =
      !q ||
      log.actor_name.toLowerCase().includes(q) ||
      log.actor_email.toLowerCase().includes(q) ||
      log.target_resource.toLowerCase().includes(q) ||
      log.ip_address.includes(q) ||
      (log.details && log.details.toLowerCase().includes(q));
    return matchesStatus && matchesAction && matchesQuery;
  });
});

function getActionLabel(action: AuditLogItem["action"]): string {
  switch (action) {
    case "USER_SUSPEND":
      return "Suspensi Pengguna";
    case "USER_ACTIVATE":
      return "Aktivasi Pengguna";
    case "USER_CREATE":
      return "Pendaftaran Pengguna";
    case "USER_UPDATE":
      return "Pembaruan Pengguna";
    case "USER_DELETE":
      return "Penghapusan Pengguna";
    case "TOKEN_ADJUST":
      return "Penyesuaian Token";
    case "ROLE_CHANGE":
      return "Perubahan Peran";
    case "CONFIG_UPDATE":
      return "Update Hyperparameter";
    case "CORPUS_INGEST":
      return "Ingestion Korpus";
    case "AUTH_LOGIN":
      return "Autentikasi Sesi";
    case "DOCUMENT_PURGE":
      return "Purge Data UU PDP";
    default:
      return action;
  }
}

function getActionBadgeVariant(action: AuditLogItem["action"]): "danger" | "secondary" | "primary" | "neutral" {
  switch (action) {
    case "USER_SUSPEND":
    case "USER_DELETE":
    case "DOCUMENT_PURGE":
      return "danger";
    case "CONFIG_UPDATE":
    case "ROLE_CHANGE":
    case "USER_UPDATE":
      return "secondary";
    case "TOKEN_ADJUST":
    case "CORPUS_INGEST":
    case "USER_CREATE":
      return "primary";
    case "USER_ACTIVATE":
    case "AUTH_LOGIN":
    default:
      return "neutral";
  }
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle overflow-hidden space-y-4">
    <!-- Header Section -->
    <div class="px-6 pt-6 pb-4 border-b border-[#ededed] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-2">
          <h2 class="text-base font-extrabold text-[#262626] tracking-tight">
            Log Jejak Audit & Forensik Keamanan
          </h2>
          <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0] italic">
            UU PDP No. 27/2022
          </span>
        </div>
        <p class="text-xs text-[#686868] mt-1 font-normal">
          Rekaman aktivitas administratif yang tidak dapat dimanipulasi (<strong class="italic font-bold text-[#262626]">immutable audit trail</strong>) untuk transparansi tata kelola.
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          type="button"
          @click="emit('refresh')"
          class="text-xs font-bold text-[#262626] bg-white hover:bg-[#fafafa] border border-[#ededed] px-3 py-1.5 rounded-[4px] shadow-audyr-subtle active:scale-[0.98] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]"
        >
          Perbarui Log
        </button>
        <button
          type="button"
          @click="emit('exportCsv')"
          class="text-xs font-bold text-white bg-[#262626] hover:bg-[#171717] px-3.5 py-1.5 rounded-[4px] shadow-audyr-subtle active:scale-[0.98] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]"
        >
          Ekspor CSV
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="px-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
      <!-- Search Input -->
      <div>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari aktor, IP, target..."
          class="w-full text-xs px-3 py-2 rounded-[4px] border border-[#ededed] bg-[#fafafa] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#262626] transition-colors duration-150 placeholder:text-[#929292]"
        />
      </div>

      <!-- Action Filter -->
      <div>
        <select
          v-model="actionFilter"
          class="w-full text-xs px-3 py-2 rounded-[4px] border border-[#ededed] bg-[#fafafa] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#262626] transition-colors duration-150 text-[#262626]"
        >
          <option value="ALL">Semua Aksi Administratif</option>
          <option value="USER_SUSPEND">Suspensi Pengguna</option>
          <option value="USER_ACTIVATE">Aktivasi Pengguna</option>
          <option value="TOKEN_ADJUST">Penyesuaian Token</option>
          <option value="ROLE_CHANGE">Perubahan Peran</option>
          <option value="CONFIG_UPDATE">Update Hyperparameter</option>
          <option value="CORPUS_INGEST">Ingestion Korpus</option>
          <option value="AUTH_LOGIN">Autentikasi Sesi</option>
          <option value="DOCUMENT_PURGE">Purge Data UU PDP</option>
        </select>
      </div>

      <!-- Status Filter -->
      <div>
        <select
          v-model="statusFilter"
          class="w-full text-xs px-3 py-2 rounded-[4px] border border-[#ededed] bg-[#fafafa] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#262626] transition-colors duration-150 text-[#262626]"
        >
          <option value="ALL">Semua Status (Sukses / Gagal)</option>
          <option value="SUCCESS">Hanya Sukses (SUCCESS)</option>
          <option value="FAILED">Hanya Gagal (FAILED)</option>
        </select>
      </div>
    </div>

    <!-- Table Section -->
    <div class="overflow-x-auto">
      <SkeletonLoader v-if="loading" :lines="6" class="p-6" />

      <table v-else-if="filteredLogs.length > 0" class="min-w-full divide-y divide-[#ededed] text-xs">
        <thead class="bg-[#fafafa]">
          <tr>
            <th scope="col" class="px-6 py-3 text-left font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Waktu (UTC+7)
            </th>
            <th scope="col" class="px-6 py-3 text-left font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Aktor Administrator
            </th>
            <th scope="col" class="px-6 py-3 text-left font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Aksi / Event
            </th>
            <th scope="col" class="px-6 py-3 text-left font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Target Sumber Daya
            </th>
            <th scope="col" class="px-6 py-3 text-left font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Alamat IP
            </th>
            <th scope="col" class="px-6 py-3 text-center font-medium text-[#686868] uppercase tracking-wider text-[11px]">
              Status
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed] bg-white">
          <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-[#fafafa] transition-colors duration-150">
            <!-- Timestamp -->
            <td class="px-6 py-3.5 whitespace-nowrap tabular-nums text-[#686868] text-[11px] font-medium">
              {{ log.timestamp }}
            </td>

            <!-- Actor -->
            <td class="px-6 py-3.5 whitespace-nowrap">
              <div class="font-bold text-[#262626]">{{ log.actor_name }}</div>
              <div class="text-[10px] text-[#737373] tabular-nums font-medium">{{ log.actor_email }}</div>
            </td>

            <!-- Action -->
            <td class="px-6 py-3.5 whitespace-nowrap">
              <Badge :variant="getActionBadgeVariant(log.action)" size="sm">
                {{ getActionLabel(log.action) }}
              </Badge>
            </td>

            <!-- Target Resource -->
            <td class="px-6 py-3.5 whitespace-nowrap text-[#262626] text-[11px]">
              <span class="px-1.5 py-0.5 rounded bg-[#f4f4f4] border border-[#e5e5e5] font-bold tabular-nums">
                {{ log.target_resource }}
              </span>
              <span v-if="log.details" class="block text-[10px] text-[#737373] mt-0.5">
                {{ log.details }}
              </span>
            </td>

            <!-- IP Address -->
            <td class="px-6 py-3.5 whitespace-nowrap tabular-nums font-bold text-[#686868] text-[11px]">
              {{ log.ip_address }}
            </td>

            <!-- Status -->
            <td class="px-6 py-3.5 whitespace-nowrap text-center">
              <span
                v-if="log.status === 'SUCCESS'"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] italic font-bold bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]"
              >
                SUCCESS
              </span>
              <span
                v-else
                class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] italic font-bold bg-[#fef2f2] text-[#991b1b] border border-[#fecaca]"
              >
                FAILED
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-else class="p-8">
        <EmptyState
          title="Tidak Ada Rekaman Log yang Sesuai"
          description="Coba ubah kata kunci pencarian atau sesuaikan filter status dan aksi administratif."
        />
      </div>
    </div>
  </div>
</template>
