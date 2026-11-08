<script setup lang="ts">
import { ref, computed } from "vue";

export interface AuditTaskItem {
  id: string;
  document_title: string;
  audit_depth: string;
  status: string;
  progress_pct: number;
  current_stage?: string | null;
  score_composite: number | null;
  created_at: string;
}

interface Props {
  tasks: AuditTaskItem[];
  loading?: boolean;
  isFullMode?: boolean;
}
const props = withDefaults(defineProps<Props>(), { loading: false, isFullMode: false });

const emit = defineEmits<{
  (e: "selectTask", taskId: string): void;
  (e: "cancelTask", taskId: string): void;
  (e: "refresh"): void;
}>();

const searchQuery = ref("");
const statusFilter = ref<"ALL" | "SUCCESS" | "PROCESSING" | "FAILED">("ALL");

const filteredTasks = computed(() =>
  props.tasks.filter((t) => {
    const q = searchQuery.value.trim().toLowerCase();
    const matchQ = !q || t.document_title.toLowerCase().includes(q) || t.id.toLowerCase().includes(q);
    const matchS =
      statusFilter.value === "ALL" ||
      (statusFilter.value === "SUCCESS" && t.status === "SUCCESS") ||
      (statusFilter.value === "PROCESSING" && (t.status === "PROCESSING" || t.status === "QUEUED")) ||
      (statusFilter.value === "FAILED" && (t.status === "FAILED" || t.status === "REVOKED"));
    return matchQ && matchS;
  })
);

function getScoreChipClass(score: number | null): string {
  if (score === null) return "bg-slate-100 text-slate-500 border-slate-200";
  if (score <= 20) return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (score <= 40) return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-rose-50 text-rose-700 border-rose-200";
}
</script>

<template>
  <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-5 font-sans select-none">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
      <div class="flex flex-wrap items-center gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-900">Riwayat Audit Naskah</h2>
          <p class="text-xs text-slate-500">Daftar pengujian dokumen yang tersimpan</p>
        </div>
        <div class="inline-flex items-center p-1 rounded-full bg-slate-100 text-xs font-semibold">
          <button v-for="st in (['ALL', 'SUCCESS', 'PROCESSING', 'FAILED'] as const)" :key="st" type="button" @click="statusFilter = st"
            class="px-3 py-1 rounded-full transition-all cursor-pointer"
            :class="statusFilter === st ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-500 hover:text-slate-900'">
            {{ st === 'ALL' ? 'Semua' : st === 'SUCCESS' ? 'Selesai' : st === 'PROCESSING' ? 'Diproses' : 'Gagal' }}
          </button>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <input v-model="searchQuery" type="text" placeholder="Cari judul..." class="px-3.5 py-1.5 rounded-full bg-slate-100 text-xs text-slate-900 border border-slate-200 focus:outline-none w-44 sm:w-56" />
        <button type="button" @click="emit('refresh')" class="inline-flex items-center px-3.5 py-1.5 rounded-full bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-800 transition-colors border border-slate-200 cursor-pointer">
          Segarkan
        </button>
      </div>
    </div>

    <div v-if="filteredTasks.length === 0" class="py-12 text-center space-y-2">
      <div class="text-sm font-bold text-slate-900">Belum Ada Riwayat Audit</div>
      <p class="text-xs text-slate-500">Unggah naskah pertama Anda pada formulir di atas untuk melihat riwayat evaluasi.</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-slate-50 text-slate-500 font-semibold border-y border-slate-100">
            <th class="py-3 px-3">Judul Naskah</th>
            <th class="py-3 px-3">ID Audit</th>
            <th class="py-3 px-3">Tanggal</th>
            <th class="py-3 px-3">Kedalaman</th>
            <th class="py-3 px-3">Status</th>
            <th class="py-3 px-3">Skor</th>
            <th class="py-3 px-3 text-right">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="task in filteredTasks" :key="task.id" class="hover:bg-slate-50 transition-colors">
            <td class="py-3.5 px-3 font-semibold text-slate-900 max-w-[240px] truncate">{{ task.document_title }}</td>
            <td class="py-3.5 px-3 text-slate-500 font-mono text-[11px]">#{{ task.id.slice(0, 8).toUpperCase() }}</td>
            <td class="py-3.5 px-3 text-slate-500 whitespace-nowrap">{{ task.created_at }}</td>
            <td class="py-3.5 px-3">
              <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold border" :class="task.audit_depth === 'FULL' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-slate-100 text-slate-600 border-slate-200'">
                {{ task.audit_depth === "FULL" ? "Hybrid" : "Leksikal" }}
              </span>
            </td>
            <td class="py-3.5 px-3">
              <span v-if="task.status === 'PROCESSING' || task.status === 'QUEUED'" class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-bold">Diproses {{ task.progress_pct }}%</span>
              <span v-else-if="task.status === 'FAILED' || task.status === 'REVOKED'" class="px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200 text-[11px] font-bold">Gagal</span>
              <span v-else class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-bold">Selesai</span>
            </td>
            <td class="py-3.5 px-3">
              <span v-if="task.score_composite !== null" class="px-2 py-0.5 rounded-full text-xs font-bold border tabular-nums" :class="getScoreChipClass(task.score_composite)">
                {{ task.score_composite.toFixed(1).replace('.', ',') }}%
              </span>
              <span v-else class="text-slate-400">&mdash;</span>
            </td>
            <td class="py-3.5 px-3 text-right whitespace-nowrap">
              <button v-if="task.status === 'PROCESSING' || task.status === 'QUEUED'" type="button" @click="emit('cancelTask', task.id)" class="text-xs font-semibold text-red-600 hover:bg-red-50 px-2.5 py-1 rounded-full cursor-pointer">Batalkan</button>
              <button v-else type="button" @click="emit('selectTask', task.id)" class="px-3 py-1 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold cursor-pointer">Buka Laporan &rarr;</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="border-t border-slate-100 pt-3 flex items-center justify-between text-xs text-slate-500">
      <span>Menampilkan 1–{{ filteredTasks.length }} dari {{ tasks.length }} audit</span>
    </div>
  </div>
</template>
