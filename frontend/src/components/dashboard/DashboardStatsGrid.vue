<script setup lang="ts">
import StatCard from "../common/StatCard.vue";

interface Props {
  tokenBalance: number;
  totalAudits: number;
  completedAudits: number;
  inProgressAudits: number;
}

withDefaults(defineProps<Props>(), {
  tokenBalance: 5,
  totalAudits: 3,
  completedAudits: 1,
  inProgressAudits: 2,
});

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Token Balance -->
    <div class="bg-white border border-[#ededed] rounded-[14px] p-5 shadow-audyr-subtle space-y-3 flex flex-col justify-between">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-semibold text-audyr-ash uppercase tracking-tight">Saldo Token Aktif</span>
        <span class="w-8 h-8 rounded-[4px] bg-[#ededed] text-audyr-ink flex items-center justify-center font-medium text-sm">
          ⚡
        </span>
      </div>
      <div>
        <div class="text-3xl font-bold font-mono text-audyr-ink tracking-tight">
          {{ tokenBalance }} <span class="text-xs font-normal text-audyr-ash font-sans">Token</span>
        </div>
        <p class="text-[11px] text-audyr-ash mt-1">Cukup untuk {{ Math.floor(tokenBalance / 2) }}x pengujian penuh</p>
      </div>
      <button
        type="button"
        @click="$emit('topup')"
        class="text-xs font-medium text-audyr-ink bg-transparent border border-[#ededed] hover:bg-[#ededed] py-1.5 px-3 rounded-[4px] transition-colors self-start"
      >
        + Top Up Kuota
      </button>
    </div>

    <!-- Total Audits -->
    <StatCard
      title="Total Naskah Diuji"
      :value="totalAudits"
      subtitle="Dokumen terdaftar di sistem"
      icon="📄"
      variant="primary"
    />

    <!-- Completed Audits -->
    <StatCard
      title="Audit Selesai"
      :value="completedAudits"
      subtitle="Laporan & Sertifikat siap unduh"
      icon="✓"
      variant="success"
    />

    <!-- In Progress -->
    <StatCard
      title="Sedang Diproses"
      :value="inProgressAudits"
      subtitle="Antrean Celery & pgvector"
      icon="⏳"
      variant="warning"
    />
  </div>
</template>
