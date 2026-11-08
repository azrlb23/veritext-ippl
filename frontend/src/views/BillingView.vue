<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { TokenBalanceCard, PlanCard, TransactionHistoryTable, TopupModal, type PlanItem, type InvoiceItem } from "../components/billing";
import { useModal, useNotification } from "../composables";
import { billingService } from "../services/billingService";
import { useAuthStore } from "../stores/auth";

const { showNotification } = useNotification();
const { isOpen: isTopupOpen, open: openTopup, close: closeTopup } = useModal();
const authStore = useAuthStore();

const balance = computed(() => authStore.tokenBalance);
const selectedPlan = ref<PlanItem | null>(null);
const isProcessing = ref(false);
const activeMode = ref<"BY_PACKAGE" | "BY_TOKEN">("BY_PACKAGE");
const customTokens = ref(5);

const packages: PlanItem[] = [
  { id: "pkg_10token", name: "Paket Starter", tokens: 15, price: "Rp 25.000", description: "15 Token untuk tugas akhir dan makalah.", popular: false },
  { id: "pkg_50token", name: "Paket Pro", tokens: 50, price: "Rp 65.000", description: "50 Token untuk revisi dan naskah panjang.", popular: true },
  { id: "pkg_200token", name: "Paket Riset Intensif", tokens: 150, price: "Rp 150.000", description: "150 Token untuk riset intensif dan naskah berulang.", popular: false },
];

const invoices = ref<InvoiceItem[]>([]);

async function loadBillingData() {
  if (!authStore.isAuthenticated) return;
  void authStore.fetchProfile();
  try {
    const [wallet, data] = await Promise.allSettled([billingService.getWallet(), billingService.listInvoices()]);
    if (wallet.status === "fulfilled" && wallet.value?.balance !== undefined) authStore.setTokenBalance(wallet.value.balance);
    if (data.status === "fulfilled" && Array.isArray(data.value)) {
      invoices.value = data.value.map((inv: any) => ({
        order_id: inv.order_id || inv.id || "-", package_name: inv.package_name || "Top-up Kuota",
        gross_amount: typeof inv.gross_amount === "number" ? `Rp ${inv.gross_amount.toLocaleString("id-ID")}` : String(inv.gross_amount || "Rp 0"),
        status: inv.status || "PENDING", payment_method: inv.payment_method || "Payment Gateway",
        date: inv.created_at ? new Date(inv.created_at).toLocaleDateString("id-ID") : "-",
      }));
    }
  } catch { /* ignore */ }
}

onMounted(() => { void loadBillingData(); });

function handleSelectPlan(plan: PlanItem) {
  selectedPlan.value = plan;
  openTopup();
}

function handleBuyCustomTokens() {
  const count = Math.max(5, customTokens.value);
  selectedPlan.value = {
    id: "pkg_10token",
    name: `Token Satuan (${count} Token)`,
    tokens: count,
    price: `Rp ${(count * 2000).toLocaleString("id-ID")}`,
    description: "Pembelian token satuan Rp 2.000 / token",
  };
  openTopup();
}

async function handleConfirmTopup(payload: { packageId: string; paymentMethod: string }) {
  if (!selectedPlan.value) return;
  isProcessing.value = true;
  try {
    const res = await billingService.topup(payload.packageId);
    closeTopup();
    showNotification(`Pesanan #${res.order_id} berhasil dibuat.`, "success");
    await loadBillingData();
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Gagal memproses pembayaran.", "error");
  } finally {
    isProcessing.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans p-4 sm:p-8 space-y-6">
    <div class="max-w-7xl mx-auto space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span class="text-[11px] font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full uppercase">Dompet Token Audit</span>
          <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mt-2">Dompet Token &amp; Kuota</h1>
          <p class="text-xs sm:text-sm text-slate-500">Kelola kuota naskah Pay-as-you-go tanpa langganan bulanan</p>
        </div>
        <div class="inline-flex p-1 rounded-full bg-slate-200/70 text-xs font-semibold">
          <button type="button" @click="activeMode = 'BY_PACKAGE'" class="px-4 py-1.5 rounded-full transition-all" :class="activeMode === 'BY_PACKAGE' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600'">Paket Bundling</button>
          <button type="button" @click="activeMode = 'BY_TOKEN'" class="px-4 py-1.5 rounded-full transition-all" :class="activeMode === 'BY_TOKEN' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600'">Token Satuan</button>
        </div>
      </div>

      <TokenBalanceCard :balance="balance" :role="authStore.role" @topup="handleSelectPlan(packages[1])" />

      <div v-if="activeMode === 'BY_PACKAGE'" class="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
        <PlanCard v-for="pkg in packages" :key="pkg.id" :plan="pkg" @select="handleSelectPlan" />
      </div>

      <div v-else class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm max-w-xl mx-auto text-center space-y-4">
        <h3 class="text-lg font-bold text-slate-900">Pembelian Token Satuan (Pay-as-you-go)</h3>
        <p class="text-xs text-slate-500">Rp 2.000 / token - Minimal pembelian 5 token (Rp 10.000)</p>
        <div class="flex items-center justify-center gap-3">
          <button type="button" @click="customTokens = Math.max(5, customTokens - 5)" class="w-9 h-9 rounded-full bg-slate-100 font-bold text-slate-800 hover:bg-slate-200">-</button>
          <span class="text-2xl font-bold text-slate-900 tabular-nums w-20 text-center">{{ customTokens }} Token</span>
          <button type="button" @click="customTokens += 5" class="w-9 h-9 rounded-full bg-slate-100 font-bold text-slate-800 hover:bg-slate-200">+</button>
        </div>
        <div class="text-sm font-semibold text-blue-600">Total: Rp {{ (customTokens * 2000).toLocaleString("id-ID") }}</div>
        <button type="button" @click="handleBuyCustomTokens" class="px-6 py-2.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm cursor-pointer">Beli Kuota Satuan &rarr;</button>
      </div>

      <TransactionHistoryTable :invoices="invoices" />
    </div>

    <TopupModal :isOpen="isTopupOpen" :selectedPackage="selectedPlan" :loading="isProcessing" @close="closeTopup" @confirm="handleConfirmTopup" />
  </div>
</template>
