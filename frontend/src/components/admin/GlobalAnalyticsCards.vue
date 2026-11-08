<script setup lang="ts">
defineProps<{
  data: {
    total_documents: number;
    avg_similarity: number;
    total_revenue: number;
    active_users: number;
  };
  loading?: boolean;
}>();

function formatCurrency(val: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val || 0);
}
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
    <!-- Total Dokumen Diaudit -->
    <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-5 sm:p-6 shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col justify-between">
      <div>
        <span class="text-xs font-semibold text-[#5B6475] uppercase tracking-wider">Total Dokumen Diaudit</span>
        <div class="mt-2.5">
          <div v-if="loading" class="h-8 w-24 bg-slate-100 rounded-lg animate-pulse" />
          <span v-else class="text-2xl sm:text-3xl font-bold text-[#0B0F19] tabular-nums tracking-tight">
            {{ (data.total_documents || 0).toLocaleString("id-ID") }}
          </span>
        </div>
      </div>
      <p class="mt-2 text-xs text-[#5B6475]">Akumulasi naskah tersimpan</p>
    </div>

    <!-- Rata-rata Kemiripan Global -->
    <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-5 sm:p-6 shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col justify-between">
      <div>
        <span class="text-xs font-semibold text-[#5B6475] uppercase tracking-wider">Rata-rata Kemiripan Global</span>
        <div class="mt-2.5">
          <div v-if="loading" class="h-8 w-20 bg-slate-100 rounded-lg animate-pulse" />
          <span v-else class="text-2xl sm:text-3xl font-bold text-[#0B0F19] tabular-nums tracking-tight">
            {{ (data.avg_similarity || 0).toFixed(1) }}%
          </span>
        </div>
      </div>
      <p class="mt-2 text-xs text-[#5B6475]">Skor komposit seluruh audit</p>
    </div>

    <!-- Total Pendapatan -->
    <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-5 sm:p-6 shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col justify-between">
      <div>
        <span class="text-xs font-semibold text-[#5B6475] uppercase tracking-wider">Total Pendapatan (IDR)</span>
        <div class="mt-2.5">
          <div v-if="loading" class="h-8 w-32 bg-slate-100 rounded-lg animate-pulse" />
          <span v-else class="text-2xl sm:text-3xl font-bold text-emerald-700 tabular-nums tracking-tight">
            {{ formatCurrency(data.total_revenue) }}
          </span>
        </div>
      </div>
      <p class="mt-2 text-xs text-[#5B6475]">Settlement Midtrans terverifikasi</p>
    </div>

    <!-- Pengguna Aktif -->
    <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl p-5 sm:p-6 shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col justify-between">
      <div>
        <span class="text-xs font-semibold text-[#5B6475] uppercase tracking-wider">Pengguna Aktif</span>
        <div class="mt-2.5">
          <div v-if="loading" class="h-8 w-20 bg-slate-100 rounded-lg animate-pulse" />
          <span v-else class="text-2xl sm:text-3xl font-bold text-[#0B0F19] tabular-nums tracking-tight">
            {{ (data.active_users || 0).toLocaleString("id-ID") }}
          </span>
        </div>
      </div>
      <p class="mt-2 text-xs text-[#5B6475]">Akun terdaftar dan berstatus aktif</p>
    </div>
  </div>
</template>
