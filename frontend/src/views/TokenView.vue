<script setup lang="ts">
import BalanceHero from "../components/token/BalanceHero.vue";
import ConfirmPurchase from "../components/token/ConfirmPurchase.vue";
import InvoiceList from "../components/token/InvoiceList.vue";
import PackageCards from "../components/token/PackageCards.vue";
import UnitPurchase from "../components/token/UnitPurchase.vue";
import { useTokenPurchase } from "../composables/useTokenPurchase";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const p = useTokenPurchase();
</script>

<template>
  <div class="mx-auto max-w-[1180px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7">
    <div class="mb-6 max-w-4xl">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Bayar yang Anda pakai, tanpa langganan.
      </h1>
    </div>
    <div class="space-y-6">
      <BalanceHero :balance="authStore.tokenBalance" :role="authStore.role" />
      <PackageCards @choose="(t) => (p.target.value = t)" />
      <UnitPurchase @choose="(t) => (p.target.value = t)" />
      <InvoiceList :invoices="p.invoices.value" />
    </div>
    <ConfirmPurchase :target="p.target.value" :processing="p.processing.value" @close="p.target.value = null" @confirm="p.confirm" />
  </div>
</template>
