<script setup lang="ts">
import Badge from "../common/Badge.vue";
import Button from "../common/Button.vue";

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
  <div v-if="activeTasks.length > 0" class="bg-white border border-[#ededed] rounded-[24px] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] space-y-5">
    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <h3 class="text-sm font-semibold text-[#17191c] uppercase tracking-wide">
          Proses Deteksi Sedang Berjalan <span class="italic font-normal text-[#777b86]">({{ activeTasks.length }} Dokumen)</span>
        </h3>
      </div>
      <Badge variant="mint" size="sm">
        Worker Celery Aktif
      </Badge>
    </div>

    <div class="space-y-4">
      <div
        v-for="task in activeTasks"
        :key="task.id"
        class="bg-[#fafafb] border border-[#ededed] rounded-[16px] p-4 sm:p-5 space-y-3"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="space-y-0.5">
            <span class="text-xs font-semibold text-[#17191c]">
              {{ task.document_title }}
            </span>
            <div class="text-[11px] text-[#777b86] flex items-center space-x-2">
              <span class="font-normal">ID: {{ task.id }}</span>
              <span>&bull;</span>
              <span class="font-normal">Kedalaman: <strong class="font-medium text-[#17191c]">{{ task.audit_depth }}</strong></span>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <span class="text-sm font-semibold text-[#17191c] tabular-nums">
              {{ task.progress_pct }}%
            </span>
            <Button
              variant="outline"
              size="xs"
              @click="emit('cancelTask', task.id)"
            >
              Batalkan
            </Button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-[#ededed] rounded-full h-2 overflow-hidden border border-[#ededed]">
          <div
            class="bg-[#17191c] h-2 rounded-full transition-[width] duration-300 ease-out"
            :style="{ width: `${task.progress_pct}%` }"
          ></div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[#777b86]">
          <span>Tahap: {{ task.current_stage || "Memproses Representasi Vektor Kalimat..." }}</span>
          <span class="italic font-normal text-[#17191c]">pgvector &amp; Rabin-Karp Pipeline</span>
        </div>
      </div>
    </div>
  </div>
</template>
