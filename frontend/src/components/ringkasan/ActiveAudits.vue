<script setup lang="ts">
import { stageLabel, type AuditTaskRow } from "../../composables/useAuditTasks";

defineProps<{ tasks: AuditTaskRow[] }>();
</script>

<template>
  <section v-if="tasks.length" class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="proses-judul">
    <h2 id="proses-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Sedang diperiksa</h2>
    <ul class="mt-5 space-y-6">
      <li v-for="t in tasks" :key="t.id">
        <div class="flex items-baseline justify-between gap-4">
          <p class="truncate text-[16px] font-semibold text-[#14111C]">{{ t.title }}</p>
          <p class="flex-shrink-0 text-[15px] font-semibold tabular-nums text-[#6D28D9]">{{ t.progress }}%</p>
        </div>
        <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-[#F3EEFA]" role="progressbar" :aria-valuenow="t.progress" aria-valuemin="0" aria-valuemax="100">
          <div class="h-full rounded-full bg-gradient-to-r from-[#8A3FE0] to-[#D26BE6] transition-[width] duration-500" :style="{ width: Math.max(t.progress, 4) + '%' }"></div>
        </div>
        <p class="mt-2 text-[14px] text-[#5E5A6B]">{{ stageLabel(t.stage) }}</p>
      </li>
    </ul>
  </section>
</template>
