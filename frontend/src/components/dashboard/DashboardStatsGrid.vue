<script setup lang="ts">
import StatCard from "../common/StatCard.vue";

interface Props {
  tokenBalance: number;
  totalAudits: number;
  completedAudits: number;
  inProgressAudits: number;
}

withDefaults(defineProps<Props>(), {
  tokenBalance: 0,
  totalAudits: 0,
  completedAudits: 0,
  inProgressAudits: 0,
});

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Token Balance -->
    <div class="bg-white border border-[#ededed] rounded-[20px] p-5 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] space-y-3 flex flex-col justify-between hover:border-[#17191c] transition-all duration-150 ease-out">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-medium text-[#777b86] uppercase tracking-wider">Saldo Token Aktif</span>
        <span class="text-[10px] font-medium tracking-wider uppercase px-2.5 py-0.5 rounded-full border border-[#ededed] bg-[#fafafb] text-[#777b86]">
          Kuota
        </span>
      </div>
      <div>
        <div class="text-3xl sm:text-4xl font-semibold text-[#17191c] tracking-tight tabular-nums">
          {{ tokenBalance }} <span class="text-xs font-normal text-[#777b86] font-sans">Token</span>
        </div>
        <p class="text-[11px] text-[#777b86] mt-1 font-normal">Cukup untuk <strong class="font-medium text-[#17191c]">{{ Math.floor(tokenBalance / 2) }}x</strong> pengujian penuh</p>
      </div>
      <button
        type="button"
        @click="$emit('topup')"
        class="text-xs font-medium text-[#17191c] bg-[#f2f2f3] hover:bg-[#17191c] hover:text-white border border-[#ededed] py-1.5 px-4 rounded-full transition-colors self-start"
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
