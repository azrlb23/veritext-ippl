<script setup lang="ts">
import StatCard from "../common/StatCard.vue";

interface Props {
  totalUsers: number;
  totalAudits: number;
  totalCorpusDocs: number;
  vectorCount: number;
  avgLatencyMs: number;
  systemLoadPct: number;
}

withDefaults(defineProps<Props>(), {
  totalUsers: 124,
  totalAudits: 842,
  totalCorpusDocs: 68,
  vectorCount: 24500,
  avgLatencyMs: 120,
  systemLoadPct: 34,
});
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <StatCard
      title="Total Pengguna"
      :value="totalUsers"
      subtitle="Pengguna terdaftar di database"
      icon="👥"
      variant="primary"
    />

    <StatCard
      title="Total Audit Dijalankan"
      :value="totalAudits"
      subtitle="Tugas Celery selesai"
      icon="⚡"
      variant="success"
    />

    <StatCard
      title="Vektor pgvector (HNSW)"
      :value="`${(vectorCount / 1000).toFixed(1)}k`"
      subtitle="384-dimensi embeddings"
      icon="🧬"
      variant="warning"
    />

    <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-2.5">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-bold text-audyr-ash uppercase tracking-wider">
          Beban Sistem & Latensi
        </span>
        <span class="w-8 h-8 rounded-[4px] bg-[#ededed] text-audyr-ink flex items-center justify-center font-bold text-sm">
          📊
        </span>
      </div>
      <div class="flex items-baseline space-x-2">
        <span class="text-2xl sm:text-3xl font-extrabold text-audyr-ink tracking-tight tabular-nums">{{ avgLatencyMs }}ms</span>
        <span class="text-xs text-audyr-ash font-bold tabular-nums">/ Beban {{ systemLoadPct }}%</span>
      </div>
      <div class="w-full bg-[#ededed] rounded-full h-1.5 overflow-hidden">
        <div class="bg-audyr-ink h-1.5 rounded-full" :style="{ width: `${systemLoadPct}%` }"></div>
      </div>
    </div>
  </div>
</template>
