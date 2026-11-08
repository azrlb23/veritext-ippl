<script setup lang="ts">
defineProps<{
  data: { total_documents: number; avg_similarity: number; total_revenue: number; active_users: number };
  loading?: boolean;
}>();

const num = (n: number) => (n || 0).toLocaleString("id-ID");
const rupiah = (n: number) => `Rp ${(n || 0).toLocaleString("id-ID")}`;
</script>

<template>
  <section class="grid grid-cols-2 gap-x-6 gap-y-9 rounded-[36px] bg-white p-7 shadow-float sm:p-10 lg:grid-cols-4" aria-label="Angka utama" :aria-busy="loading">
    <div>
      <p class="text-[40px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[52px]">{{ loading ? "-" : num(data.total_documents) }}</p>
      <p class="mt-3 text-[14px] text-[#5E5A6B]">naskah diperiksa</p>
    </div>
    <div>
      <p class="text-[40px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[52px]">{{ loading ? "-" : (data.avg_similarity || 0).toFixed(1).replace(".", ",") + "%" }}</p>
      <p class="mt-3 text-[14px] text-[#5E5A6B]">rata-rata kemiripan</p>
    </div>
    <div>
      <p class="text-[40px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[52px]">{{ loading ? "-" : num(data.active_users) }}</p>
      <p class="mt-3 text-[14px] text-[#5E5A6B]">pengguna aktif</p>
    </div>
    <div>
      <p class="vt-accent text-[28px] font-semibold leading-[1.15] tracking-[-0.04em] tabular-nums sm:text-[34px]">{{ loading ? "-" : rupiah(data.total_revenue) }}</p>
      <p class="mt-3 text-[14px] text-[#5E5A6B]">pendapatan</p>
    </div>
  </section>
</template>
