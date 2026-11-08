<script setup lang="ts">
import { rupiah, type InvoiceRow } from "../../composables/useTokenPurchase";

defineProps<{ invoices: InvoiceRow[] }>();
const label = (s: string) => ({ PAID: "Lunas", PENDING: "Menunggu pembayaran", EXPIRED: "Kedaluwarsa", FAILED: "Gagal", CANCEL: "Dibatalkan" } as Record<string, string>)[s] || s;
const tone = (s: string) => (s === "PAID" ? "text-[#047857]" : s === "PENDING" ? "text-[#6D28D9]" : "text-[#B91C1C]");
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="tagihan-judul">
    <h3 id="tagihan-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Riwayat pembelian</h3>
    <p v-if="invoices.length === 0" class="py-10 text-center text-[15px] text-[#5E5A6B]">Belum ada pembelian token.</p>
    <ul v-else class="mt-3 divide-y divide-[#14111C]/[0.06]">
      <li v-for="i in invoices" :key="i.orderId" class="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
        <div class="min-w-0">
          <p class="truncate text-[16px] font-semibold text-[#14111C]">{{ i.name }}</p>
          <p class="text-[14px] text-[#5E5A6B]">{{ i.date }} <span aria-hidden="true">&middot;</span> {{ i.orderId }}</p>
        </div>
        <div class="flex items-baseline justify-between gap-6 sm:justify-end">
          <p class="text-[16px] font-semibold tabular-nums text-[#14111C]">{{ rupiah(i.amount) }}</p>
          <p class="min-w-[150px] text-[14px] font-medium sm:text-right" :class="tone(i.status)">{{ label(i.status) }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>
