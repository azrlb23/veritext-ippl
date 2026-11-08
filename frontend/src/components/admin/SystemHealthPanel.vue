<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  health: {
    database_status: string;
    db_latency_ms: number;
    total_vector_chunks: number;
    redis_status: string;
    celery_active_tasks: number;
    total_audits: number;
    total_corpus_docs: number;
  };
  loading?: boolean;
}>();

const ok = (s?: string) => ["HEALTHY", "OPERATIONAL", "RUNNING"].includes((s || "").toUpperCase());
const num = (n: number) => (n || 0).toLocaleString("id-ID");
const rows = computed(() => [
  { label: "Basis data", value: ok(props.health.database_status) ? "Normal" : "Terganggu", good: ok(props.health.database_status), hint: `${(props.health.db_latency_ms || 0).toFixed(1).replace(".", ",")} ms` },
  { label: "Antrean pemeriksaan", value: ok(props.health.redis_status) ? "Normal" : "Terganggu", good: ok(props.health.redis_status), hint: `${num(props.health.celery_active_tasks)} tugas berjalan` },
  { label: "Pemeriksaan tercatat", value: num(props.health.total_audits), good: true, hint: "" },
  { label: "Dokumen pembanding", value: num(props.health.total_corpus_docs), good: true, hint: `${num(props.health.total_vector_chunks)} potongan makna` },
]);
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="sehat-judul" :aria-busy="loading">
    <h2 id="sehat-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Kondisi sistem</h2>
    <dl class="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="r in rows" :key="r.label" class="rounded-[24px] bg-[#F3EEFA] p-5">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">{{ r.label }}</dt>
        <dd class="mt-2 text-[24px] font-semibold tracking-[-0.03em] tabular-nums" :class="r.good ? 'text-[#14111C]' : 'text-[#B91C1C]'">{{ loading ? "-" : r.value }}</dd>
        <p v-if="r.hint" class="mt-1 text-[13px] text-[#5E5A6B]">{{ r.hint }}</p>
      </div>
    </dl>
  </section>
</template>
