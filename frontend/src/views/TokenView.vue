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
  <div class="mx-auto max-w-[1180px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-9 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Token</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Bayar yang Anda pakai, <span class="vt-accent">tanpa langganan.</span>
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
