<script setup lang="ts">
import { ref } from "vue";
import {
  TokenBalanceCard,
  PlanCard,
  TransactionHistoryTable,
  TopupModal,
  type PlanItem,
  type InvoiceItem,
} from "../components/billing";
import { useModal, useNotification } from "../composables";

const { showNotification } = useNotification();
const { isOpen: isTopupOpen, open: openTopup, close: closeTopup } = useModal();

const balance = ref(5);
const selectedPlan = ref<PlanItem | null>(null);
const isProcessing = ref(false);

const packages: PlanItem[] = [
  {
    id: "pkg_10token",
    name: "Paket Mahasiswa",
    tokens: 10,
    price: "Rp 25.000",
    description: "Cocok untuk pemeriksaan tugas akhir, makalah, atau artikel ilmiah semesteran.",
    popular: false,
  },
  {
    id: "pkg_50token",
    name: "Paket Peneliti",
    tokens: 50,
    price: "Rp 100.000",
    description: "Ideal untuk dosen pembimbing, reviewer jurnal, dan pengujian berkala tesis.",
    popular: true,
  },
  {
    id: "pkg_200token",
    name: "Paket Institusi",
    tokens: 200,
    price: "Rp 350.000",
    description: "Dirancang untuk program studi, laboratorium riset, dan tim penjaminan mutu.",
    popular: false,
  },
];

const invoices = ref<InvoiceItem[]>([
  {
    order_id: "VT-20261011-9F2B81C4",
    package_name: "Paket Mahasiswa (10 Token)",
    gross_amount: "Rp 25.000",
    status: "PAID",
    payment_method: "GoPay / QRIS",
    date: "11 Okt 2026",
  },
  {
    order_id: "VT-20260920-1A87D09E",
    package_name: "Paket Peneliti (50 Token)",
    gross_amount: "Rp 100.000",
    status: "PAID",
    payment_method: "BCA Virtual Account",
    date: "20 Sep 2026",
  },
]);

function handleSelectPlan(plan: PlanItem) {
  selectedPlan.value = plan;
  openTopup();
}

function handleConfirmTopup(payload: { packageId: string; paymentMethod: string }) {
  if (!selectedPlan.value) return;
  isProcessing.value = true;

  setTimeout(() => {
    const pkg = selectedPlan.value!;
    balance.value += pkg.tokens;

    const newInvoice: InvoiceItem = {
      order_id: `VT-${Date.now().toString(16).toUpperCase()}`,
      package_name: `${pkg.name} (${pkg.tokens} Token)`,
      gross_amount: pkg.price,
      status: "PAID",
      payment_method: payload.paymentMethod.toUpperCase(),
      date: "Hari ini",
    };
    invoices.value.unshift(newInvoice);

    isProcessing.value = false;
    closeTopup();

    showNotification(
      `Pembayaran berhasil! Kuota ${pkg.tokens} token telah ditambahkan ke dompet Anda.`,
      "success",
      "Top Up Sukses"
    );
  }, 900);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
    <!-- Wallet Overview Card -->
    <TokenBalanceCard
      :balance="balance"
      @topup="handleSelectPlan(packages[1])"
    />

    <!-- Pricing Packages Grid -->
    <div class="space-y-6">
      <div class="text-center max-w-xl mx-auto space-y-1">
        <h2 class="text-2xl font-extrabold text-audyr-ink tracking-tight">
          Pilihan Paket Top-Up Token
        </h2>
        <p class="text-xs text-audyr-ash">
          Pilih paket kuota audit sesuai kebutuhan pengujian naskah akademik Anda tanpa biaya langganan berulang (<span class="italic font-bold text-audyr-ink">Pay-as-you-go</span>).
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <PlanCard
          v-for="pkg in packages"
          :key="pkg.id"
          :plan="pkg"
          @select="handleSelectPlan"
        />
      </div>
    </div>

    <!-- Invoices & Transaction History -->
    <TransactionHistoryTable :invoices="invoices" />

    <!-- Topup Confirmation & Midtrans Modal -->
    <TopupModal
      :isOpen="isTopupOpen"
      :selectedPackage="selectedPlan"
      :loading="isProcessing"
      @close="closeTopup"
      @confirm="handleConfirmTopup"
    />
  </div>
</template>
