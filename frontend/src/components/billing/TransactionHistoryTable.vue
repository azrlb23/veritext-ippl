<script setup lang="ts">
import EmptyState from "../common/EmptyState.vue";

export interface InvoiceItem {
  order_id: string;
  package_name: string;
  gross_amount: string;
  status: string;
  payment_method: string;
  date: string;
}

interface Props {
  invoices: InvoiceItem[];
}

defineProps<Props>();

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case "PAID":
      return "bg-[#EAF7EE] text-[#15803D] border-[#A7F3D0]";
    case "PENDING":
      return "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]";
    case "EXPIRED":
    case "FAILED":
    case "CANCEL":
      return "bg-[#FEF2F2] text-[#B91C1C] border-[#FECACA]";
    default:
      return "bg-[#F1F5F9] text-[#5B6475] border-[#E4E8F0]";
  }
}
</script>

<template>
  <div class="bg-[#F8FAFC] border border-[#E4E8F0] rounded-[28px] overflow-hidden p-6 sm:p-8 space-y-5 font-sans select-none">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm sm:text-base font-bold uppercase tracking-tight text-[#0B0F19]">
          Riwayat Pembelian &amp; Faktur
        </h3>
        <p class="text-xs text-[#5B6475] mt-0.5 font-normal">Daftar transaksi pengisian kuota token akun Anda</p>
      </div>
      <span class="text-xs text-[#5B6475] font-semibold tabular-nums px-3 py-1 bg-white border border-[#E4E8F0] rounded-full shadow-2xs">
        Total: {{ invoices.length }} transaksi
      </span>
    </div>

    <div v-if="invoices.length === 0" class="py-6">
      <EmptyState
        title="Belum Ada Transaksi"
        description="Riwayat faktur pembelian token akan dicatat secara otomatis di sini setelah transaksi pertama."
      />
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs sm:text-[13px]">
        <thead>
          <tr class="bg-white border-y border-[#E4E8F0] text-[#5B6475] font-semibold uppercase text-[11px] tracking-tight">
            <th class="py-3 px-4">Nomor Pesanan (Order ID)</th>
            <th class="py-3 px-4">Paket</th>
            <th class="py-3 px-4">Nominal</th>
            <th class="py-3 px-4">Metode Pembayaran</th>
            <th class="py-3 px-4">Status</th>
            <th class="py-3 px-4">Waktu</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#E4E8F0]">
          <tr v-for="inv in invoices" :key="inv.order_id" class="hover:bg-white transition-colors">
            <td class="py-3.5 px-4 font-mono font-semibold tabular-nums text-[#0B0F19]">{{ inv.order_id }}</td>
            <td class="py-3.5 px-4 font-medium text-[#0B0F19]">{{ inv.package_name }}</td>
            <td class="py-3.5 px-4 font-bold tabular-nums text-[#0B0F19]">{{ inv.gross_amount }}</td>
            <td class="py-3.5 px-4 text-[#5B6475]">{{ inv.payment_method }}</td>
            <td class="py-3.5 px-4">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wide"
                :class="getStatusBadgeClass(inv.status)"
              >
                {{ inv.status }}
              </span>
            </td>
            <td class="py-3.5 px-4 text-[#5B6475] tabular-nums whitespace-nowrap">{{ inv.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
