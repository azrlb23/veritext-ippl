<script setup lang="ts">
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
  (e: "viewAll"): void;
}>();
</script>

<template>
  <div
    class="bg-white rounded-[28px] sm:rounded-[36px] border border-white/80 p-6 sm:p-7 shadow-[0_16px_48px_rgba(138,152,184,0.18)] space-y-5 font-sans select-none h-full flex flex-col justify-between"
  >
    <!-- Header -->
    <div class="flex items-center justify-between pb-3 border-b border-[#E4E8F0]">
      <div class="space-y-0.5">
        <h2 class="text-xl sm:text-2xl font-bold text-[#0B0F19]">
          Antrean Deteksi
        </h2>
        <p class="text-xs text-[#5B6475]">Pemeriksaan paralel Celery worker</p>
      </div>
      <button
        v-if="activeTasks.length > 0"
        type="button"
        @click="emit('viewAll')"
        class="text-xs font-semibold text-[#1560BD] hover:text-[#1A73D9] transition-colors cursor-pointer px-3 py-1 bg-[#EAF3FE] rounded-full border border-[#BFDBFE]"
      >
        {{ activeTasks.length }} tugas aktif &rarr;
      </button>
      <span v-else class="text-xs text-[#5B6475] font-semibold px-3 py-1 bg-[#F3F6FC] rounded-full">
        0 tugas aktif
      </span>
    </div>

    <!-- Empty State -->
    <div
      v-if="activeTasks.length === 0"
      class="py-12 text-center text-xs text-[#5B6475] space-y-2"
    >
      <div class="w-10 h-10 rounded-full bg-[#F3F6FC] flex items-center justify-center text-[#5B6475] mx-auto">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <p class="font-medium text-[#0B0F19]">Tidak Ada Antrean Deteksi</p>
      <p class="text-[11px] text-[#5B6475]">Semua tugas audit naskah telah selesai diproses.</p>
    </div>

    <!-- Active Tasks List -->
    <div v-else class="space-y-4 flex-1">
      <div
        v-for="task in activeTasks"
        :key="task.id"
        class="space-y-2.5 bg-[#F8FAFC] p-4 rounded-[20px] border border-[#E4E8F0]"
      >
        <!-- Title & Cancel Link -->
        <div class="flex items-start justify-between gap-3">
          <div class="space-y-0.5">
            <h3 class="text-xs sm:text-sm font-bold text-[#0B0F19] truncate max-w-[200px] sm:max-w-[280px]">
              {{ task.document_title }}
            </h3>
            <p class="text-[11.5px] text-[#5B6475]">
              {{ task.current_stage || "Tahap 2 - Penelusuran sumber internet publik (Google Search Grounding)" }}
            </p>
          </div>

          <button
            type="button"
            @click="emit('cancelTask', task.id)"
            class="text-[11px] font-semibold text-[#B91C1C] hover:bg-[#FEF2F2] px-2.5 py-1 rounded-full transition-all cursor-pointer flex-shrink-0 active:scale-[0.98]"
          >
            Batalkan
          </button>
        </div>

        <!-- Progress Bar & Percentage -->
        <div class="flex items-center gap-3 pt-1">
          <div class="w-full bg-[#E2E8F0] rounded-full h-2 overflow-hidden">
            <div
              class="bg-[#1560BD] h-2 rounded-full transition-all duration-500 ease-out shadow-xs"
              :style="{ width: `${task.progress_pct}%` }"
            ></div>
          </div>
          <span class="text-xs font-bold text-[#0B0F19] tabular-nums font-mono">
            {{ task.progress_pct }}%
          </span>
        </div>
      </div>
    </div>

    <!-- Bottom summary status -->
    <div class="pt-3 border-t border-[#E4E8F0] text-[11px] text-[#5B6475] flex items-center justify-between">
      <span>Worker: Celery Redis Broker</span>
      <span class="flex items-center gap-1.5 text-[#15803D] font-semibold">
        <span class="w-1.5 h-1.5 rounded-full bg-[#15803D] animate-pulse"></span>
        Sistem Siaga
      </span>
    </div>
  </div>
</template>
