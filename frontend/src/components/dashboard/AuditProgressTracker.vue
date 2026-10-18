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
  <div v-if="activeTasks.length > 0" class="bg-white border border-[#ededed] rounded-[14px] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-[#262626] animate-pulse"></span>
        <h3 class="text-sm font-extrabold text-[#262626] uppercase tracking-wide">
          Proses Deteksi Sedang Berjalan <span class="italic font-bold text-[#515151]">({{ activeTasks.length }} Dokumen)</span>
        </h3>
      </div>
      <Badge variant="mint" size="sm" dot dotPulse>
        Worker Celery Aktif
      </Badge>
    </div>

    <div class="space-y-4">
      <div
        v-for="task in activeTasks"
        :key="task.id"
        class="bg-[#fafafa] border border-[#ededed] rounded-[8px] p-4 space-y-3"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="space-y-0.5">
            <span class="text-xs font-bold text-[#262626]">
              {{ task.document_title }}
            </span>
            <div class="text-[11px] text-[#737373] flex items-center space-x-2">
              <span class="font-medium">ID: {{ task.id }}</span>
              <span>&bull;</span>
              <span class="font-medium">Kedalaman: <strong class="font-bold text-[#262626]">{{ task.audit_depth }}</strong></span>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <span class="text-sm font-extrabold text-[#262626] tabular-nums">
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
            class="bg-[#262626] h-2 rounded-full transition-[width] duration-300 ease-out"
            :style="{ width: `${task.progress_pct}%` }"
          ></div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[#737373]">
          <span>Tahap: {{ task.current_stage || "Memproses Representasi Vektor Kalimat..." }}</span>
          <span class="italic font-bold text-[#262626]">pgvector &amp; Rabin-Karp Pipeline</span>
        </div>
      </div>
    </div>
  </div>
</template>
