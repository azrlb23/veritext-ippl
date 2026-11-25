<script setup lang="ts">
import { ref } from "vue";
import { rupiah, type InvoiceRow } from "../../composables/useTokenPurchase";
import { useNotification } from "../../composables/useNotification";
import { billingService } from "../../services/billingService";

defineProps<{ invoices: InvoiceRow[] }>();
const { showNotification } = useNotification();
const downloading = ref<string | null>(null);
const label = (s: string) => ({ PAID: "Lunas", PENDING: "Menunggu pembayaran", EXPIRED: "Kedaluwarsa", FAILED: "Gagal", CANCEL: "Dibatalkan" } as Record<string, string>)[s] || s;
const tone = (s: string) => (s === "PAID" ? "text-[#047857]" : s === "PENDING" ? "text-[#0F766E]" : "text-[#B91C1C]");

async function downloadReceipt(orderId: string) {
  if (!orderId || orderId === "-") return;
  downloading.value = orderId;
  try {
    await billingService.downloadInvoicePdf(orderId);
  } catch {
    showNotification("Kuitansi PDF belum bisa diunduh.", "error");
  } finally {
    downloading.value = null;
  }
}
</script>

<template>
  <section class="pt-2" aria-labelledby="tagihan-judul">
    <h3 id="tagihan-judul" class="text-[19px] font-semibold tracking-[-0.025em] text-[#14111C]">Riwayat pembelian</h3>
    <p v-if="invoices.length === 0" class="py-10 text-center text-[14.5px] text-[#5E5A6B]">Belum ada pembelian token.</p>
    <ul v-else class="mt-3 divide-y divide-[#E6ECEB]">
      <li v-for="i in invoices" :key="i.orderId" class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
        <div class="min-w-0">
          <p class="truncate text-[15.5px] font-semibold text-[#14111C]">{{ i.name }}</p>
          <p class="text-[13.5px] text-[#5E5A6B]">{{ i.date }} ({{ i.orderId }})</p>
        </div>
        <div class="flex flex-wrap items-center justify-between gap-4 sm:justify-end">
          <p class="text-[15.5px] font-semibold tabular-nums text-[#14111C]">{{ rupiah(i.amount) }}</p>
          <p class="min-w-[130px] text-[13.5px] font-medium sm:text-right" :class="tone(i.status)">{{ label(i.status) }}</p>
          <button
            type="button"
            :disabled="downloading === i.orderId"
            class="vt-btn-light inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-50"
            @click="downloadReceipt(i.orderId)"
          >{{ downloading === i.orderId ? "Mengunduh..." : "Unduh kuitansi" }}</button>
        </div>
      </li>
    </ul>
  </section>
</template>
