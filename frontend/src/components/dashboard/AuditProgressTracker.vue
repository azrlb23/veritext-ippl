<script setup lang="ts">
import Badge from "../common/Badge.vue";

export interface ActiveAuditTask {
  id: string;
  document_title: string;
  progress_pct: number;
  current_stage?: string;
  audit_depth: string;
}

interface Props {
  activeTasks: ActiveAuditTask[];
}

defineProps<Props>();

const emit = defineEmits<{
  (e: "cancelTask", taskId: string): void;
}>();
</script>

<template>
  <div
    v-if="activeTasks.length > 0"
    class="bg-white border border-[#ededed] rounded-[22px] p-6 sm:p-7 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] space-y-5"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-[#17191c]"></span>
        <h3 class="text-xs font-semibold text-[#17191c] uppercase tracking-wider">
          Proses Deteksi Sedang Berjalan <span class="italic font-normal text-[#777b86]">({{ activeTasks.length }} Dokumen)</span>
        </h3>
      </div>
      <Badge variant="mint" size="sm">
        Worker Celery Aktif
      </Badge>
    </div>

    <div class="space-y-3.5">
      <div
        v-for="task in activeTasks"
        :key="task.id"
        class="bg-[#fafafb] border border-[#ededed] rounded-[18px] p-4 sm:p-5 space-y-3 hover:border-[#17191c] transition-colors"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="space-y-0.5">
            <span class="text-xs font-semibold text-[#17191c]">
              {{ task.document_title }}
            </span>
            <div class="text-[11px] text-[#777b86] flex items-center space-x-2 font-mono">
              <span class="font-normal">ID: {{ task.id.slice(0, 12) }}...</span>
              <span>&bull;</span>
              <span class="font-normal font-sans">Kedalaman: <strong class="font-medium text-[#17191c]">{{ task.audit_depth }}</strong></span>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <span class="text-sm font-bold text-[#17191c] tabular-nums font-mono">
              {{ task.progress_pct }}%
            </span>
            <button
              type="button"
              @click="emit('cancelTask', task.id)"
              class="px-3.5 py-1 text-xs font-medium text-[#777b86] hover:text-[#17191c] hover:bg-[#ededed] rounded-full border border-[#ededed] transition-colors active:scale-[0.98]"
            >
              Batalkan
            </button>
          </div>
        </div>

        <!-- Progress Bar with Peach Accent -->
        <div class="w-full bg-[#ededed] rounded-full h-1.5 overflow-hidden">
          <div
            class="bg-[#17191c] h-1.5 rounded-full transition-[width] duration-300 ease-out"
            :style="{ width: `${task.progress_pct}%` }"
          ></div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[#777b86]">
          <span class="truncate max-w-sm">Tahap: {{ task.current_stage || "Memproses Representasi Vektor Kalimat..." }}</span>
          <span class="italic font-normal text-[#17191c] flex-shrink-0">pgvector &amp; Rabin-Karp</span>
        </div>
      </div>
    </div>
  </div>
</template>
