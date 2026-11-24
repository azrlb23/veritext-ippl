<script setup lang="ts">
import type { InvoiceSummary } from "../../types/admin";

defineProps<{ summary: InvoiceSummary; loading?: boolean }>();

const num = (n: number) => (n || 0).toLocaleString("id-ID");
const rupiah = (n: number) => `Rp ${(n || 0).toLocaleString("id-ID")}`;
</script>

<template>
  <section class="rounded-[28px] border border-[#E8ECEB] bg-white p-6 sm:p-8" aria-labelledby="inv-summary-title" :aria-busy="loading">
    <h2 id="inv-summary-title" class="text-[20px] font-semibold tracking-[-0.03em] text-[#14111C]">Ringkasan transaksi</h2>
    <dl class="mt-5 grid grid-cols-2 gap-x-6 gap-y-5 divide-[#E8ECEB] sm:grid-cols-3 lg:grid-cols-5 lg:gap-0 lg:divide-x">
      <div class="lg:pr-6">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Total pendapatan</dt>
        <dd class="mt-2 text-[22px] font-semibold tracking-[-0.03em] tabular-nums text-[#0F766E]">
          {{ loading ? "-" : rupiah(summary.total_revenue) }}
        </dd>
      </div>
      <div class="lg:px-6">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Lunas</dt>
        <dd class="mt-2 text-[24px] font-semibold tracking-[-0.03em] tabular-nums text-[#047857]">
          {{ loading ? "-" : num(summary.paid) }}
        </dd>
      </div>
      <div class="lg:px-6">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Menunggu</dt>
        <dd class="mt-2 text-[24px] font-semibold tracking-[-0.03em] tabular-nums text-[#0F766E]">
          {{ loading ? "-" : num(summary.pending) }}
        </dd>
      </div>
      <div class="lg:px-6">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Gagal</dt>
        <dd class="mt-2 text-[24px] font-semibold tracking-[-0.03em] tabular-nums text-[#B91C1C]">
          {{ loading ? "-" : num(summary.failed) }}
        </dd>
      </div>
      <div class="col-span-2 sm:col-span-1 lg:pl-6">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Paket terlaris</dt>
        <dd class="mt-2 truncate text-[18px] font-semibold tracking-[-0.02em] text-[#14111C]">
          {{ loading ? "-" : summary.top_package || "-" }}
        </dd>
      </div>
    </dl>
  </section>
</template>
