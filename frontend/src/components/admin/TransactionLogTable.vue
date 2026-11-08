<script setup lang="ts">
interface TransactionItem {
  id?: string;
  order_id: string;
  gross_amount: number;
  status: string;
  paid_at?: string | null;
  created_at?: string | null;
}

defineProps<{
  transactions: TransactionItem[];
  loading?: boolean;
}>();

function formatCurrency(val: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val || 0);
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "-";
  try {
    return new Date(dateStr).toLocaleString("id-ID", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return dateStr;
  }
}

function getStatusBadgeClass(status: string): string {
  const norm = (status || "").toLowerCase();
  if (norm === "settlement" || norm === "capture" || norm === "paid") {
    return "bg-emerald-50 text-emerald-700 border-emerald-200";
  }
  if (norm === "pending") {
    return "bg-amber-50 text-amber-800 border-amber-200";
  }
  return "bg-rose-50 text-rose-700 border-rose-200";
}
</script>

<template>
  <div class="bg-white border border-[#E4E8F0] rounded-2xl sm:rounded-3xl overflow-hidden shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col h-full">
    <div class="px-5 sm:px-6 py-4 sm:py-5 border-b border-[#E4E8F0] flex items-center justify-between">
      <div>
        <h3 class="text-sm sm:text-base font-bold text-[#0B0F19]">Riwayat Transaksi Midtrans</h3>
        <p class="text-xs text-[#5B6475] mt-0.5">Catatan pesanan dan pembayaran via Snap Gateway</p>
      </div>
      <span class="text-xs font-semibold text-[#5B6475] tabular-nums">{{ transactions.length }} transaksi terbaru</span>
    </div>

    <div class="overflow-x-auto flex-grow">
      <table class="w-full text-left text-xs border-collapse" aria-label="Tabel riwayat transaksi pembayaran Midtrans">
        <caption class="sr-only">Daftar transaksi pembayaran top-up kuota audit VeriText AI via Midtrans Snap</caption>
        <thead class="bg-slate-50/70 text-[#5B6475] border-b border-[#E4E8F0] font-semibold uppercase tracking-wider">
          <tr>
            <th scope="col" class="py-3 px-4 sm:px-5">Order ID</th>
            <th scope="col" class="py-3 px-4">Nominal (IDR)</th>
            <th scope="col" class="py-3 px-4">Status</th>
            <th scope="col" class="py-3 px-4 sm:px-5">Waktu</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#E4E8F0] text-slate-700">
          <template v-if="loading">
            <tr v-for="i in 4" :key="`skeleton-tx-${i}`" class="animate-pulse">
              <td class="py-3.5 px-4 sm:px-5"><div class="h-4 bg-slate-100 rounded w-24" /></td>
              <td class="py-3.5 px-4"><div class="h-4 bg-slate-100 rounded w-20" /></td>
              <td class="py-3.5 px-4"><div class="h-4 bg-slate-100 rounded w-16" /></td>
              <td class="py-3.5 px-4 sm:px-5"><div class="h-4 bg-slate-100 rounded w-28" /></td>
            </tr>
          </template>
          <tr v-else-if="transactions.length === 0">
            <td colspan="4" class="py-12 text-center">
              <p class="text-sm font-semibold text-[#0B0F19]">Tidak ada transaksi pembayaran</p>
              <p class="text-xs text-[#5B6475] mt-1">Belum ada riwayat transaksi Midtrans yang tercatat di sistem.</p>
            </td>
          </tr>
          <tr v-for="tx in transactions" :key="tx.order_id || tx.id" class="hover:bg-slate-50/80 transition-colors duration-150">
            <td class="py-3 px-4 sm:px-5 font-mono font-medium text-[#0B0F19]">{{ tx.order_id || "-" }}</td>
            <td class="py-3 px-4 font-semibold text-[#0B0F19] tabular-nums">{{ formatCurrency(tx.gross_amount) }}</td>
            <td class="py-3 px-4">
              <span :class="['px-2.5 py-0.5 rounded-full text-[11px] font-bold border uppercase tracking-wider', getStatusBadgeClass(tx.status)]">
                {{ tx.status?.toUpperCase() || "UNKNOWN" }}
              </span>
            </td>
            <td class="py-3 px-4 sm:px-5 font-mono text-[#5B6475] tabular-nums">{{ formatDate(tx.paid_at || tx.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
