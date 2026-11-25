<script setup lang="ts">
import { stageLabel, type AuditTaskRow } from "../../composables/useAuditTasks";

defineProps<{ tasks: AuditTaskRow[] }>();
</script>

<template>
  <section v-if="tasks.length" class="border-b border-[#E6ECEB] pb-7" aria-labelledby="proses-judul">
    <h2 id="proses-judul" class="text-[19px] font-semibold tracking-[-0.025em] text-[#14111C]">Sedang diperiksa</h2>
    <ul class="mt-4 space-y-5">
      <li v-for="t in tasks" :key="t.id">
        <div class="flex items-baseline justify-between gap-4">
          <p class="truncate text-[15.5px] font-semibold text-[#14111C]">{{ t.title }}</p>
          <p class="flex-shrink-0 text-[14.5px] font-semibold tabular-nums text-[#0F766E]">{{ t.progress }}%</p>
        </div>
        <div class="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-[#E6F2F0]" role="progressbar" :aria-valuenow="t.progress" aria-valuemin="0" aria-valuemax="100">
          <div class="h-full rounded-full bg-gradient-to-r from-[#0F766E] to-[#14B8A6] transition-[width] duration-500" :style="{ width: Math.max(t.progress, 4) + '%' }"></div>
        </div>
        <p class="mt-1.5 text-[13.5px] text-[#5E5A6B]">{{ stageLabel(t.stage) }}</p>
      </li>
    </ul>
  </section>
</template>
