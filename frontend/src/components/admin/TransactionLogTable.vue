<script setup lang="ts">
interface TransactionItem {
  id?: string;
  order_id: string;
  gross_amount: number;
  status: string;
  paid_at?: string | null;
  created_at?: string | null;
}

defineProps<{ transactions: TransactionItem[]; loading?: boolean }>();

const rupiah = (n: number) => `Rp ${(n || 0).toLocaleString("id-ID")}`;
const date = (d?: string | null) => (d ? new Date(d).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" }) : "-");
const label = (s: string) => ({ PAID: "Lunas", PENDING: "Menunggu", EXPIRED: "Kedaluwarsa", FAILED: "Gagal", CANCEL: "Dibatalkan", CHALLENGE: "Ditinjau" } as Record<string, string>)[s] || s;
const tone = (s: string) => (s === "PAID" ? "text-[#047857]" : s === "PENDING" ? "text-[#6D28D9]" : "text-[#B91C1C]");
</script>

<template>
  <section class="h-full rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="trx-judul" :aria-busy="loading">
    <h2 id="trx-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Transaksi terbaru</h2>
    <p v-if="!loading && transactions.length === 0" class="py-12 text-center text-[15px] text-[#5E5A6B]">Belum ada transaksi.</p>
    <ul v-else class="mt-3 divide-y divide-[#14111C]/[0.06]">
      <li v-for="t in transactions" :key="t.order_id" class="flex items-center justify-between gap-4 py-4">
        <div class="min-w-0">
          <p class="truncate text-[15px] font-semibold text-[#14111C]">{{ t.order_id }}</p>
          <p class="text-[13px] text-[#5E5A6B]">{{ date(t.paid_at || t.created_at) }}</p>
        </div>
        <div class="flex-shrink-0 text-right">
          <p class="text-[16px] font-semibold tabular-nums text-[#14111C]">{{ rupiah(t.gross_amount) }}</p>
          <p class="text-[13px] font-medium" :class="tone(t.status)">{{ label(t.status) }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>
