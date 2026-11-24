<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useAdminData, useSectionReveal } from "../composables";
import { InvoiceSummary, TransactionLogTable } from "../components/admin";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { loading, error, invoices, invoiceSummary, invoicesMeta, fetchInvoices } = useAdminData();

const selectedStatus = ref("");
const page = ref(1);

function loadInvoices() {
  void fetchInvoices({ status: selectedStatus.value, page: page.value });
}

function handleStatus(status: string) {
  selectedStatus.value = status;
  page.value = 1;
  loadInvoices();
}

function handlePage(nextPage: number) {
  page.value = nextPage;
  loadInvoices();
}

onMounted(loadInvoices);
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1180px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Riwayat pembayaran dan paket.
      </h1>
      <button type="button" :disabled="loading" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-50" @click="loadInvoices">
        {{ loading ? "Memuat..." : "Muat ulang" }}
      </button>
    </div>

    <div v-if="error && !loading" class="vt-reveal mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ error }}</p>
      <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold" @click="loadInvoices">Coba lagi</button>
    </div>

    <div class="space-y-6">
      <div class="vt-reveal vt-d-1"><InvoiceSummary :summary="invoiceSummary" :loading="loading" /></div>
      <div class="vt-reveal vt-d-2">
        <TransactionLogTable
          :transactions="invoices"
          :loading="loading"
          :page="invoicesMeta.page"
          :pages="invoicesMeta.pages"
          :total="invoicesMeta.total"
          :selected-status="selectedStatus"
          @update:selected-status="handleStatus"
          @change-page="handlePage"
        />
      </div>
    </div>
  </div>
</template>
