<script setup lang="ts">
interface HealthData {
  database_status: string;
  db_latency_ms: number;
  total_vector_chunks: number;
  redis_status: string;
  celery_active_tasks: number;
  total_audits: number;
  total_corpus_docs: number;
}

defineProps<{
  health: HealthData;
  loading?: boolean;
}>();

function getStatusBadge(status?: string): { label: string; class: string } {
  const norm = (status || "").toUpperCase();
  if (norm === "HEALTHY" || norm === "OPERATIONAL" || norm === "RUNNING") {
    return { label: "OPERASIONAL", class: "bg-emerald-50 text-emerald-700 border-emerald-200" };
  }
  return { label: norm || "TERGANGGU", class: "bg-amber-50 text-amber-800 border-amber-200" };
}
</script>

<template>
  <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-6 sm:p-7 shadow-[0_4px_20px_rgba(138,152,184,0.06)] space-y-5">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E4E8F0] gap-3">
      <div>
        <h3 class="text-base font-bold text-[#0B0F19]">Telemetri Infrastruktur &amp; Antrean Mesin</h3>
        <p class="text-xs text-[#5B6475] mt-0.5">Pemantauan kesehatan komputasi PostgreSQL, pgvector, Redis, dan Celery</p>
      </div>
      <span class="inline-flex self-start sm:self-auto text-[11px] font-semibold text-[#1560BD] bg-[#EAF3FE] border border-[#BFDBFE] px-3 py-1 rounded-full uppercase tracking-wider">
        100% Read-Only Monitoring
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
      <!-- PostgreSQL / pgvector -->
      <div class="border border-[#E4E8F0] rounded-xl sm:rounded-2xl p-4 sm:p-5 bg-slate-50/50 flex flex-col justify-between space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-[#0B0F19]">PostgreSQL + pgvector</span>
          <span :class="['px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider', getStatusBadge(health.database_status).class]">
            {{ getStatusBadge(health.database_status).label }}
          </span>
        </div>
        <div class="space-y-2 text-xs text-[#5B6475]">
          <div class="flex justify-between items-center">
            <span>Latensi Kueri:</span>
            <div v-if="loading" class="h-4 w-12 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19] tabular-nums">{{ health.db_latency_ms || 0 }} ms</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Vektor Terindeks:</span>
            <div v-if="loading" class="h-4 w-16 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19] tabular-nums">{{ (health.total_vector_chunks || 0).toLocaleString("id-ID") }} chunks</span>
          </div>
        </div>
      </div>

      <!-- Redis & Celery -->
      <div class="border border-[#E4E8F0] rounded-xl sm:rounded-2xl p-4 sm:p-5 bg-slate-50/50 flex flex-col justify-between space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-[#0B0F19]">Redis &amp; Celery Broker</span>
          <span :class="['px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider', getStatusBadge(health.redis_status).class]">
            {{ getStatusBadge(health.redis_status).label }}
          </span>
        </div>
        <div class="space-y-2 text-xs text-[#5B6475]">
          <div class="flex justify-between items-center">
            <span>Status Broker:</span>
            <div v-if="loading" class="h-4 w-14 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19]">{{ health.redis_status || "UNKNOWN" }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Tugas Aktif Celery:</span>
            <div v-if="loading" class="h-4 w-12 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19] tabular-nums">{{ health.celery_active_tasks || 0 }} tugas</span>
          </div>
        </div>
      </div>

      <!-- Volume & Storage -->
      <div class="border border-[#E4E8F0] rounded-xl sm:rounded-2xl p-4 sm:p-5 bg-slate-50/50 flex flex-col justify-between space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-[#0B0F19]">Volume Repositori</span>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border bg-blue-50 text-blue-700 border-blue-200 uppercase tracking-wider">
            SINKRON
          </span>
        </div>
        <div class="space-y-2 text-xs text-[#5B6475]">
          <div class="flex justify-between items-center">
            <span>Total Tugas Audit:</span>
            <div v-if="loading" class="h-4 w-12 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19] tabular-nums">{{ (health.total_audits || 0).toLocaleString("id-ID") }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Naskah Korpus:</span>
            <div v-if="loading" class="h-4 w-14 bg-slate-200 rounded animate-pulse" />
            <span v-else class="font-mono font-semibold text-[#0B0F19] tabular-nums">{{ (health.total_corpus_docs || 0).toLocaleString("id-ID") }} naskah</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
