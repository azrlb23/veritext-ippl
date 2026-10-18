<script setup lang="ts">
import Badge from "../common/Badge.vue";
import Button from "../common/Button.vue";
import EmptyState from "../common/EmptyState.vue";
import SkeletonLoader from "../common/SkeletonLoader.vue";

export interface AuditTaskItem {
  id: string;
  document_title: string;
  audit_depth: string;
  status: string;
  progress_pct: number;
  score_composite: number | null;
  created_at: string;
}

interface Props {
  tasks: AuditTaskItem[];
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "selectTask", taskId: string): void;
  (e: "refresh"): void;
}>();

function getStatusVariant(status: string): "success" | "primary" | "warning" | "danger" | "neutral" {
  switch (status) {
    case "SUCCESS":
      return "success";
    case "PROCESSING":
      return "primary";
    case "QUEUED":
      return "warning";
    case "FAILED":
    case "REVOKED":
    case "CANCELLED":
      return "danger";
    default:
      return "neutral";
  }
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden space-y-4">
    <div class="p-5 border-b border-[#ededed] flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold text-[#262626] uppercase tracking-wide">
          Riwayat Tugas Audit Terakhir
        </h3>
        <p class="text-xs text-[#737373] mt-0.5">Daftar naskah akademik yang telah diuji oleh sistem</p>
      </div>

      <div class="flex items-center space-x-3">
        <span class="text-xs text-[#737373] font-mono">Total: {{ tasks.length }} dokumen</span>
        <Button
          variant="outline"
          size="xs"
          @click="emit('refresh')"
        >
          ↻ Refresh
        </Button>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="p-6">
      <SkeletonLoader shape="table-row" :count="4" />
    </div>

    <!-- Empty State -->
    <div v-else-if="tasks.length === 0" class="p-8">
      <EmptyState
        icon="📑"
        title="Belum Ada Riwayat Audit"
        description="Silakan unggah naskah pertama Anda pada formulir di atas untuk memulai deteksi plagiarisme."
      />
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-[#fafafa] border-y border-[#ededed] text-[#515151] font-medium uppercase tracking-wider text-[11px]">
            <th class="py-3 px-5">Nama Dokumen</th>
            <th class="py-3 px-4">Kedalaman</th>
            <th class="py-3 px-4">Status & Progres</th>
            <th class="py-3 px-4">Skor Komposit</th>
            <th class="py-3 px-4">Waktu</th>
            <th class="py-3 px-5 text-right">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="hover:bg-[#fafafa] transition-colors duration-150 ease-out"
          >
            <td class="py-3.5 px-5 font-medium text-[#262626] max-w-xs truncate" :title="task.document_title">
              {{ task.document_title }}
            </td>

            <td class="py-3.5 px-4">
              <Badge
                :variant="task.audit_depth === 'FULL' ? 'primary' : 'neutral'"
                size="xs"
              >
                {{ task.audit_depth }}
              </Badge>
            </td>

            <td class="py-3.5 px-4">
              <div class="flex items-center space-x-2">
                <Badge
                  :variant="getStatusVariant(task.status)"
                  size="xs"
                  dot
                  :dotPulse="task.status === 'PROCESSING'"
                >
                  {{ task.status }}
                </Badge>
                <span v-if="task.status === 'PROCESSING'" class="text-[10px] text-audyr-ash font-mono">
                  ({{ task.progress_pct }}%)
                </span>
              </div>
            </td>

            <td class="py-3.5 px-4 font-mono font-bold">
              <span
                v-if="task.score_composite !== null"
                :class="task.score_composite > 25 ? 'text-amber-700' : 'text-[#065f46]'"
              >
                {{ task.score_composite.toFixed(1) }}%
              </span>
              <span v-else class="text-audyr-ash">&mdash;</span>
            </td>

            <td class="py-3.5 px-4 text-audyr-ash whitespace-nowrap">
              {{ task.created_at }}
            </td>

            <td class="py-3.5 px-5 text-right whitespace-nowrap">
              <Button
                variant="outline"
                size="xs"
                @click="emit('selectTask', task.id)"
              >
                Lihat Laporan
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
