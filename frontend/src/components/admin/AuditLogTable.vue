<script setup lang="ts">
interface AuditLogItem {
  id: string;
  action_type: string;
  actor_ip?: string | null;
  action_result: string;
  created_at: string;
}

defineProps<{
  logs: AuditLogItem[];
  loading?: boolean;
  page: number;
  pages: number;
  total: number;
  selectedAction?: string;
}>();

const emit = defineEmits<{
  (e: "update:selectedAction", val: string): void;
  (e: "changePage", val: number): void;
}>();

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "-";
  try {
    return new Date(dateStr).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return dateStr;
  }
}
</script>

<template>
  <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl overflow-hidden shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col h-full">
    <div class="px-5 sm:px-6 py-4 sm:py-5 border-b border-[#E4E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h3 class="text-sm sm:text-base font-bold text-[#0B0F19]">Log Audit Keamanan</h3>
        <p class="text-xs text-[#5B6475] mt-0.5">Total {{ total.toLocaleString("id-ID") }} catatan kepatuhan</p>
      </div>
      <div class="flex items-center gap-2">
        <label for="admin-action-filter" class="text-xs text-[#5B6475] font-semibold">Aksi:</label>
        <select
          id="admin-action-filter"
          :value="selectedAction || ''"
          @change="emit('update:selectedAction', ($event.target as HTMLSelectElement).value)"
          class="text-xs border border-[#E4E8F0] rounded-lg px-2.5 py-1.5 bg-white text-[#0B0F19] focus:outline-none focus:ring-1 focus:ring-[#1560BD]"
        >
          <option value="">Semua Aksi</option>
          <option value="AUTH_LOGIN">AUTH_LOGIN</option>
          <option value="DOCUMENT_PURGE">DOCUMENT_PURGE</option>
          <option value="AUDIT_SUBMIT">AUDIT_SUBMIT</option>
          <option value="TOKEN_DEBIT">TOKEN_DEBIT</option>
          <option value="BILLING_TOPUP">BILLING_TOPUP</option>
        </select>
      </div>
    </div>

    <div class="overflow-x-auto flex-grow">
      <table class="w-full text-left text-xs border-collapse" aria-label="Tabel log audit keamanan dan kepatuhan sistem">
        <caption class="sr-only">Catatan audit jejak aktivitas sistem</caption>
        <thead class="bg-slate-50/70 text-[#5B6475] border-b border-[#E4E8F0] font-semibold uppercase tracking-wider">
          <tr>
            <th scope="col" class="py-3 px-4 sm:px-5">Waktu</th>
            <th scope="col" class="py-3 px-4">Tipe Aksi</th>
            <th scope="col" class="py-3 px-4">IP Aktor</th>
            <th scope="col" class="py-3 px-4 sm:px-5">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#E4E8F0] text-slate-700">
          <template v-if="loading">
            <tr v-for="i in 4" :key="`skeleton-log-${i}`" class="animate-pulse">
              <td class="py-3.5 px-4 sm:px-5"><div class="h-4 bg-slate-100 rounded w-28" /></td>
              <td class="py-3.5 px-4"><div class="h-4 bg-slate-100 rounded w-24" /></td>
              <td class="py-3.5 px-4"><div class="h-4 bg-slate-100 rounded w-20" /></td>
              <td class="py-3.5 px-4 sm:px-5"><div class="h-4 bg-slate-100 rounded w-16" /></td>
            </tr>
          </template>
          <tr v-else-if="logs.length === 0">
            <td colspan="4" class="py-12 text-center">
              <p class="text-sm font-semibold text-[#0B0F19]">Tidak ada log aktivitas</p>
              <p class="text-xs text-[#5B6475] mt-1">Tidak ada catatan aktivitas yang cocok dengan kriteria filter.</p>
            </td>
          </tr>
          <tr v-for="item in logs" :key="item.id" class="hover:bg-slate-50/80 transition-colors duration-150">
            <td class="py-3 px-4 sm:px-5 font-mono text-[#5B6475] tabular-nums">{{ formatDate(item.created_at) }}</td>
            <td class="py-3 px-4 font-mono text-[11px] font-semibold text-[#0B0F19]">
              <span class="bg-slate-100 px-2 py-0.5 rounded border border-[#E4E8F0]">{{ item.action_type }}</span>
            </td>
            <td class="py-3 px-4 font-mono text-[#5B6475]">{{ item.actor_ip || "-" }}</td>
            <td class="py-3 px-4 sm:px-5">
              <span :class="['px-2.5 py-0.5 rounded-full text-[11px] font-bold border uppercase tracking-wider', item.action_result?.toUpperCase() === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200']">
                {{ item.action_result?.toUpperCase() || "UNKNOWN" }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="px-5 sm:px-6 py-3.5 border-t border-[#E4E8F0] bg-slate-50/50 flex items-center justify-between text-xs text-[#5B6475]">
      <span class="tabular-nums">Halaman {{ page }} dari {{ pages || 1 }}</span>
      <div class="flex gap-2">
        <button
          type="button"
          :disabled="page <= 1 || loading"
          @click="emit('changePage', page - 1)"
          class="px-3 py-1.5 border border-[#E4E8F0] rounded-lg bg-white font-medium hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98] transition-colors transition-transform duration-150 shadow-xs cursor-pointer"
        >
          Sebelumnya
        </button>
        <button
          type="button"
          :disabled="page >= pages || loading"
          @click="emit('changePage', page + 1)"
          class="px-3 py-1.5 border border-[#E4E8F0] rounded-lg bg-white font-medium hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98] transition-colors transition-transform duration-150 shadow-xs cursor-pointer"
        >
          Selanjutnya
        </button>
      </div>
    </div>
  </div>
</template>
