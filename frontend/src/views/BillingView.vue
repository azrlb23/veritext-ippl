<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  TokenBalanceCard,
  PlanCard,
  TransactionHistoryTable,
  TopupModal,
  type PlanItem,
  type InvoiceItem,
} from "../components/billing";
import { useModal, useNotification } from "../composables";
import { billingService } from "../services/billingService";
import { useAuthStore } from "../stores/auth";

const { showNotification } = useNotification();
const { isOpen: isTopupOpen, open: openTopup, close: closeTopup } = useModal();
const authStore = useAuthStore();

const balance = computed(() => authStore.tokenBalance);
const selectedPlan = ref<PlanItem | null>(null);
const isProcessing = ref(false);
const isLoading = ref(false);

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

const invoices = ref<InvoiceItem[]>([]);

async function loadBillingData() {
  isLoading.value = true;
  try {
    if (authStore.isAuthenticated) {
      void authStore.fetchProfile();
      try {
        const wallet = await billingService.getWallet();
        if (wallet && typeof wallet.balance === "number") {
          authStore.setTokenBalance(wallet.balance);
        }
      } catch {
        // Continue to load invoices
      }
    }

    const data = await billingService.listInvoices();
    if (Array.isArray(data)) {
      invoices.value = data.map((inv: any) => ({
        order_id: inv.order_id || inv.id || "-",
        package_name: inv.package_name || "Top-up Kuota",
        gross_amount: typeof inv.gross_amount === "number"
          ? `Rp ${inv.gross_amount.toLocaleString("id-ID")}`
          : String(inv.gross_amount || "Rp 0"),
        status: inv.status || "PENDING",
        payment_method: inv.payment_type || inv.payment_method || "Payment Gateway",
        date: inv.created_at
          ? new Date(inv.created_at).toLocaleDateString("id-ID", { dateStyle: "medium" })
          : "-",
      }));
    }
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memuat data transaksi.",
      "error"
    );
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  void loadBillingData();
});

function handleSelectPlan(plan: PlanItem) {
  selectedPlan.value = plan;
  openTopup();
}

async function handleConfirmTopup(payload: { packageId: string; paymentMethod: string }) {
  if (!selectedPlan.value) return;
  isProcessing.value = true;

  try {
    const res = await billingService.topup(payload.packageId);
    closeTopup();
    showNotification(
      `Order top-up ${selectedPlan.value.name} berhasil dibuat. ID Pesanan: ${res.order_id}.`,
      "success",
      "Top Up Dimulai"
    );
    await loadBillingData();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memproses permintaan top up.",
      "error"
    );
  } finally {
    isProcessing.value = false;
  }
}
</script>

<template>
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
    <!-- Ambient Warm Peach Radial Aura (Steep Signature Glow) -->
    <div
      class="absolute top-0 left-1/2 -translate-x-1/2 -z-10 w-full max-w-6xl h-[450px] bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(251,225,209,0.5),rgba(255,255,255,0))] blur-3xl pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Editorial Header -->
    <div class="space-y-2">
      <div class="flex items-center space-x-2">
        <span class="text-[10px] uppercase font-bold tracking-wider text-[#5d2a1a] bg-[#fbe1d1] px-2.5 py-0.5 rounded-full">
          Billing &amp; Token Balance
        </span>
      </div>
      <h1 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Dompet Token &amp; Kuota Audit Akademik
      </h1>
      <p class="text-xs sm:text-sm text-[#777b86] max-w-2xl font-normal leading-relaxed">
        Kelola saldo token Anda untuk menguji naskah ilmiah melalui <strong class="font-medium text-[#17191c]">Hybrid 4-Tier Pipeline</strong> tanpa biaya langganan berulang (<span class="italic font-medium text-[#17191c]">Pay-as-you-go</span>).
      </p>
    </div>

    <!-- Wallet Overview Card -->
    <TokenBalanceCard
      :balance="balance"
      :role="authStore.role"
      @topup="handleSelectPlan(packages[1])"
    />

    <!-- Pricing Packages Grid -->
    <div class="space-y-8">
      <div class="text-center max-w-xl mx-auto space-y-2">
        <h2 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight">
          Pilihan Paket Top-Up Kuota
        </h2>
        <p class="text-xs text-[#777b86] font-normal leading-relaxed">
          Pilih paket kuota audit sesuai intensitas pengujian naskah akademik Anda. Token berlaku selamanya dan dapat digunakan kapan saja.
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
