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
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle overflow-hidden p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
          Riwayat Pembelian & Faktur
        </h3>
        <p class="text-xs text-audyr-ash mt-0.5">Daftar transaksi pengisian kuota token akun Anda</p>
      </div>
      <span class="text-xs text-audyr-ash font-mono">Total: {{ invoices.length }} transaksi</span>
    </div>

    <div v-if="invoices.length === 0" class="py-6">
      <EmptyState
        icon="💳"
        title="Belum Ada Transaksi"
        description="Riwayat faktur pembelian token akan dicatat secara otomatis di sini."
      />
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-white border-y border-[#ededed] text-audyr-ash font-medium uppercase text-[11px] tracking-tight">
            <th class="py-3 px-4">Nomor Pesanan (Order ID)</th>
            <th class="py-3 px-4">Paket</th>
            <th class="py-3 px-4">Nominal</th>
            <th class="py-3 px-4">Metode Pembayaran</th>
            <th class="py-3 px-4">Status</th>
            <th class="py-3 px-4">Waktu</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr v-for="inv in invoices" :key="inv.order_id" class="hover:bg-[#fafafa] transition-colors">
            <td class="py-3.5 px-4 font-mono font-medium text-audyr-ink">{{ inv.order_id }}</td>
            <td class="py-3.5 px-4 text-audyr-slate">{{ inv.package_name }}</td>
            <td class="py-3.5 px-4 font-mono font-bold text-audyr-ink">{{ inv.gross_amount }}</td>
            <td class="py-3.5 px-4 text-audyr-ash">{{ inv.payment_method }}</td>
            <td class="py-3.5 px-4">
              <Badge :variant="getStatusVariant(inv.status)" size="xs">
                {{ inv.status }}
              </Badge>
            </td>
            <td class="py-3.5 px-4 text-audyr-ash font-mono">{{ inv.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
