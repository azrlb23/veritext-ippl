<script setup lang="ts">
import type { AdminTransactionItem } from "../../types/admin";

defineProps<{
  transactions: AdminTransactionItem[];
  loading?: boolean;
  page?: number;
  pages?: number;
  total?: number;
  selectedStatus?: string;
}>();

const emit = defineEmits<{
  (e: "update:selectedStatus", v: string): void;
  (e: "changePage", v: number): void;
}>();

const STATUS_FILTERS = [
  { key: "", label: "Semua" },
  { key: "PAID", label: "Lunas" },
  { key: "PENDING", label: "Menunggu" },
  { key: "FAILED", label: "Gagal" },
];

const LABELS: Record<string, string> = {
  PAID: "Lunas",
  SETTLEMENT: "Lunas",
  PENDING: "Menunggu",
  EXPIRED: "Kedaluwarsa",
  FAILED: "Gagal",
  CANCEL: "Dibatalkan",
  CHALLENGE: "Ditinjau",
};

const norm = (s: string) => (s || "").toUpperCase();
const rupiah = (n: number) => `Rp ${(n || 0).toLocaleString("id-ID")}`;
const date = (d?: string | null) => (d ? new Date(d).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" }) : "-");
const label = (s: string) => LABELS[norm(s)] || s;
const tone = (s: string) => {
  const st = norm(s);
  if (st === "PAID" || st === "SETTLEMENT") return "text-[#047857]";
  if (st === "PENDING") return "text-[#0F766E]";
  return "text-[#B91C1C]";
};
const title = (t: AdminTransactionItem) =>
  t.package_name ? `${t.package_name}${t.token_amount ? ` (${t.token_amount} token)` : ""}` : t.order_id;
const navCls = "vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-semibold transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-40";
</script>

<template>
  <section class="h-full rounded-[28px] border border-[#E8ECEB] bg-white p-6 sm:p-8" aria-labelledby="trx-judul" :aria-busy="loading">
    <h2 id="trx-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Transaksi terbaru</h2>
    <p v-if="typeof total === 'number'" class="mt-1 text-[14px] tabular-nums text-[#5E5A6B]">{{ total.toLocaleString("id-ID") }} transaksi</p>

    <div class="mt-4 flex flex-wrap gap-2" role="group" aria-label="Saring status transaksi">
      <button
        v-for="f in STATUS_FILTERS"
        :key="f.key"
        type="button"
        :aria-pressed="(selectedStatus || '') === f.key"
        class="inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13px] font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        :class="(selectedStatus || '') === f.key ? 'vt-btn-dark' : 'vt-btn-light'"
        @click="emit('update:selectedStatus', f.key)"
      >
        {{ f.label }}
      </button>
    </div>

    <p v-if="!loading && transactions.length === 0" class="py-12 text-center text-[15px] text-[#5E5A6B]">Belum ada transaksi.</p>
    <ul v-else class="mt-3 divide-y divide-[#E8ECEB]">
      <li v-for="t in transactions" :key="t.order_id" class="flex items-center justify-between gap-4 py-4">
        <div class="min-w-0">
          <p class="truncate text-[15px] font-semibold text-[#14111C]">{{ title(t) }}</p>
          <p class="truncate text-[13px] text-[#5E5A6B]">{{ t.order_id }} - {{ date(t.paid_at || t.created_at) }}</p>
        </div>
        <div class="flex-shrink-0 text-right">
          <p class="text-[16px] font-semibold tabular-nums text-[#14111C]">{{ rupiah(t.gross_amount) }}</p>
          <p class="text-[13px] font-medium" :class="tone(t.status)">{{ label(t.status) }}</p>
        </div>
      </li>
    </ul>

    <div v-if="(pages || 1) > 1" class="mt-5 flex items-center justify-between gap-3">
      <button type="button" :class="navCls" :disabled="(page || 1) <= 1" @click="emit('changePage', (page || 1) - 1)">Sebelumnya</button>
      <span class="text-[14px] tabular-nums text-[#5E5A6B]">{{ page || 1 }} / {{ pages }}</span>
      <button type="button" :class="navCls" :disabled="(page || 1) >= (pages || 1)" @click="emit('changePage', (page || 1) + 1)">Berikutnya</button>
    </div>
  </section>
</template>
