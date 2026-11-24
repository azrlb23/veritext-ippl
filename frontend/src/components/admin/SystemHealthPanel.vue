<script setup lang="ts">
import { computed } from "vue";
import type { SystemHealthMetrics } from "../../types/admin";

const props = defineProps<{ health: SystemHealthMetrics; loading?: boolean }>();

const ok = (s?: string) => ["HEALTHY", "OPERATIONAL", "RUNNING"].includes((s || "").toUpperCase());
const num = (n: number) => (n || 0).toLocaleString("id-ID");

const rows = computed(() => {
  const dbOk = ok(props.health.database_status);
  const redisOk = ok(props.health.redis_status);
  return [
    {
      label: "Basis data",
      value: dbOk ? "Normal" : "Terganggu",
      tone: dbOk ? "text-[#0F766E]" : "text-[#B91C1C]",
      hint: `${(props.health.db_latency_ms || 0).toFixed(1).replace(".", ",")} ms`,
    },
    {
      label: "Antrean pemeriksaan",
      value: redisOk ? "Normal" : "Terganggu",
      tone: redisOk ? "text-[#0F766E]" : "text-[#B91C1C]",
      hint: `${num(props.health.celery_active_tasks)} berjalan, ${num(props.health.queue_depth || 0)} mengantre`,
    },
    {
      label: "Pemeriksaan tercatat",
      value: num(props.health.total_audits),
      tone: "text-[#14111C]",
      hint: "",
    },
    {
      label: "Dokumen pembanding",
      value: num(props.health.total_corpus_docs),
      tone: "text-[#14111C]",
      hint: `${num(props.health.total_vector_chunks)} potongan makna`,
    },
  ];
});
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="sehat-judul" :aria-busy="loading">
    <h2 id="sehat-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Kondisi sistem</h2>
    <dl class="mt-5 grid grid-cols-1 divide-y divide-[#E8ECEB] sm:grid-cols-2 sm:gap-x-6 sm:divide-y-0 lg:grid-cols-4 lg:gap-0 lg:divide-x lg:divide-[#E8ECEB]">
      <div v-for="r in rows" :key="r.label" class="py-4 first:pt-0 last:pb-0 sm:py-3 lg:px-6 lg:py-1 lg:first:pl-0 lg:last:pr-0">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">{{ r.label }}</dt>
        <dd class="mt-2 text-[24px] font-semibold tracking-[-0.03em] tabular-nums" :class="loading ? 'text-[#14111C]' : r.tone">
          {{ loading ? "-" : r.value }}
        </dd>
        <p v-if="r.hint" class="mt-1 text-[13px] text-[#5E5A6B]">{{ r.hint }}</p>
      </div>
    </dl>
  </section>
</template>
