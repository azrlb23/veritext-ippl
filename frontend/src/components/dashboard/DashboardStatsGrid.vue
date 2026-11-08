<script setup lang="ts">
interface Props {
  tokenBalance: number;
  totalAudits: number;
  completedAudits: number;
  inProgressAudits: number;
  avgScore?: number;
}

withDefaults(defineProps<Props>(), {
  tokenBalance: 0,
  totalAudits: 0,
  completedAudits: 0,
  inProgressAudits: 0,
  avgScore: 24.1,
});

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5 font-sans select-none">
    
    <!-- CARD 1: Saldo Token (Hero Gradient Blue Card) -->
    <div
      class="rounded-[26px] sm:rounded-[28px] p-6 bg-gradient-to-br from-[#1A73D9] to-[#1560BD] text-white shadow-[0_12px_32px_rgba(21,96,189,0.25)] flex flex-col justify-between space-y-4 relative overflow-hidden transition-all duration-200"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-white/90">Saldo Token</span>
        <button
          type="button"
          @click="$emit('topup')"
          class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-[#1560BD] shadow-sm hover:scale-105 active:scale-95 transition-transform cursor-pointer"
          title="Top up saldo token"
        >
          <!-- Coin / Plus Icon -->
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-6-6h12" />
          </svg>
        </button>
      </div>

      <div class="space-y-1">
        <div class="flex items-baseline gap-2.5">
          <span class="text-4xl sm:text-[42px] font-extrabold text-white tracking-[-0.8px] tabular-nums">
            {{ tokenBalance }}
          </span>
          <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#0B0F19]/25 text-white">
            Tersedia
          </span>
        </div>
        <div class="text-xs text-white/80 font-normal">
          Kuota aktif untuk pengujian naskah
        </div>
      </div>
    </div>

    <!-- CARD 2: Naskah Diuji -->
    <div
      class="rounded-[26px] sm:rounded-[28px] p-6 bg-white border border-white/80 shadow-[0_8px_28px_rgba(138,152,184,0.12)] flex flex-col justify-between space-y-4 transition-all duration-200"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-[#5B6475]">Naskah Diuji</span>
        <div class="w-10 h-10 rounded-full bg-[#0B0F19] flex items-center justify-center text-white shadow-sm">
          <!-- Document Icon -->
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex items-baseline gap-2.5">
          <span class="text-4xl sm:text-[42px] font-extrabold text-[#0B0F19] tracking-[-0.8px] tabular-nums">
            {{ totalAudits }}
          </span>
          <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#F3F6FC] text-[#5B6475]">
            Total Berkas
          </span>
        </div>
        <div class="text-xs text-[#5B6475] font-normal">
          Riwayat naskah yang telah diuji
        </div>
      </div>
    </div>

    <!-- CARD 3: Audit Selesai -->
    <div
      class="rounded-[26px] sm:rounded-[28px] p-6 bg-white border border-white/80 shadow-[0_8px_28px_rgba(138,152,184,0.12)] flex flex-col justify-between space-y-4 transition-all duration-200"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-[#5B6475]">Audit Selesai</span>
        <div class="w-10 h-10 rounded-full bg-[#EAF7EE] flex items-center justify-center text-[#15803D] border border-[#A7F3D0] shadow-sm">
          <!-- Checkmark Icon -->
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex items-baseline gap-2.5">
          <span class="text-4xl sm:text-[42px] font-extrabold text-[#0B0F19] tracking-[-0.8px] tabular-nums">
            {{ completedAudits }}
          </span>
          <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#EAF7EE] text-[#15803D]">
            Lengkap
          </span>
        </div>
        <div class="text-xs text-[#5B6475] font-normal">
          Laporan diagnostik siap diakses
        </div>
      </div>
    </div>

    <!-- CARD 4: Rata-rata Skor -->
    <div
      class="rounded-[26px] sm:rounded-[28px] p-6 bg-white border border-white/80 shadow-[0_8px_28px_rgba(138,152,184,0.12)] flex flex-col justify-between space-y-4 transition-all duration-200"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-[#5B6475]">Rata-rata Skor</span>
        <div class="w-10 h-10 rounded-full bg-[#EAF3FE] flex items-center justify-center text-[#1560BD] border border-[#BFDBFE] shadow-sm">
          <!-- Gauge Icon -->
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l2.5 2.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex items-baseline gap-2.5">
          <span class="text-4xl sm:text-[42px] font-extrabold text-[#0B0F19] tracking-[-0.8px] tabular-nums">
            {{ avgScore.toFixed(1).replace('.', ',') }}%
          </span>
          <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#EAF7EE] text-[#15803D]">
            Batas Aman
          </span>
        </div>
        <div class="text-xs text-[#5B6475] font-normal">
          Di bawah ambang 20% toleransi
        </div>
      </div>
    </div>

  </div>
</template>
