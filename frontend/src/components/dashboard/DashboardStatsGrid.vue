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
        <span class="text-[11px] font-bold text-audyr-ash uppercase tracking-wider">Saldo Token Aktif</span>
        <span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded border border-[#ededed] bg-[#fafafa] text-[#515151]">
          Kuota
        </span>
      </div>
      <div>
        <div class="text-3xl sm:text-4xl font-extrabold text-[#262626] tracking-tight tabular-nums">
          {{ tokenBalance }} <span class="text-xs font-normal text-audyr-ash font-sans">Token</span>
        </div>
        <p class="text-[11px] text-audyr-ash mt-1 font-normal">Cukup untuk <strong class="font-bold text-[#262626]">{{ Math.floor(tokenBalance / 2) }}x</strong> pengujian penuh</p>
      </div>
      <button
        type="button"
        @click="$emit('topup')"
        class="text-xs font-bold text-audyr-ink bg-transparent border border-[#ededed] hover:bg-[#ededed] py-1.5 px-3 rounded-[4px] transition-colors self-start"
      >
        + Top Up Kuota
      </button>
    </div>

    <!-- Total Audits -->
    <StatCard
      title="Total Naskah Diuji"
      :value="totalAudits"
      subtitle="Dokumen terdaftar di sistem"
      badge="Dokumen"
      variant="primary"
    />

    <!-- Completed Audits -->
    <StatCard
      title="Audit Selesai"
      :value="completedAudits"
      subtitle="Laporan & Sertifikat siap unduh"
      badge="Selesai"
      variant="success"
    />

    <!-- In Progress -->
    <StatCard
      title="Sedang Diproses"
      :value="inProgressAudits"
      subtitle="Antrean Celery & pgvector"
      badge="Antrean"
      variant="warning"
    />
  </div>
</template>
