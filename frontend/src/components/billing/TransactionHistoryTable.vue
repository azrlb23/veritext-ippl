<script setup lang="ts">
import Badge from "../common/Badge.vue";
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

function getStatusVariant(status: string): "success" | "warning" | "danger" | "neutral" {
  switch (status) {
    case "PAID":
      return "success";
    case "PENDING":
      return "warning";
    case "EXPIRED":
    case "FAILED":
    case "CANCEL":
      return "danger";
    default:
      return "neutral";
  }
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[24px] shadow-[0_0_0_1px_rgba(4,23,43,0.05)] overflow-hidden p-6 sm:p-8 space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-tight text-[#17191c]">
          Riwayat Pembelian &amp; Faktur
        </h3>
        <p class="text-xs text-[#777b86] mt-0.5 font-normal">Daftar transaksi pengisian kuota token akun Anda</p>
      </div>
      <span class="text-xs text-[#777b86] font-normal tabular-nums">Total: {{ invoices.length }} transaksi</span>
    </div>

    <div v-if="invoices.length === 0" class="py-6">
      <EmptyState
        title="Belum Ada Transaksi"
        description="Riwayat faktur pembelian token akan dicatat secara otomatis di sini."
      />
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-[#fafafb] border-y border-[#ededed] text-[#777b86] font-medium uppercase text-[11px] tracking-tight">
            <th class="py-3 px-4">Nomor Pesanan (Order ID)</th>
            <th class="py-3 px-4">Paket</th>
            <th class="py-3 px-4">Nominal</th>
            <th class="py-3 px-4">Metode Pembayaran</th>
            <th class="py-3 px-4">Status</th>
            <th class="py-3 px-4">Waktu</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr v-for="inv in invoices" :key="inv.order_id" class="hover:bg-[#fafafb] transition-colors">
            <td class="py-3.5 px-4 font-medium tabular-nums text-[#17191c]">{{ inv.order_id }}</td>
            <td class="py-3.5 px-4 text-[#777b86]">{{ inv.package_name }}</td>
            <td class="py-3.5 px-4 font-semibold tabular-nums text-[#17191c]">{{ inv.gross_amount }}</td>
            <td class="py-3.5 px-4 text-[#777b86]">{{ inv.payment_method }}</td>
            <td class="py-3.5 px-4">
              <Badge :variant="getStatusVariant(inv.status)" size="xs">
                {{ inv.status }}
              </Badge>
            </td>
            <td class="py-3.5 px-4 text-[#777b86] tabular-nums">{{ inv.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
