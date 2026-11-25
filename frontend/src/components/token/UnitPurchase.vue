<script setup lang="ts">
import { computed, ref } from "vue";
import { UNIT_MIN, UNIT_PRICE, rupiah, type PurchaseTarget } from "../../composables/useTokenPurchase";

const emit = defineEmits<{ (e: "choose", t: PurchaseTarget): void }>();
const count = ref(UNIT_MIN);
const total = computed(() => count.value * UNIT_PRICE);
const step = (d: number) => (count.value = Math.min(500, Math.max(UNIT_MIN, count.value + d)));
const stepBtn = "vt-btn-light flex h-12 w-12 cursor-pointer items-center justify-center rounded-full text-[22px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]";
</script>

<template>
  <section class="flex flex-col gap-5 border-y border-[#E6ECEB] py-6 lg:flex-row lg:items-center lg:justify-between" aria-labelledby="satuan-judul">
    <div class="max-w-md">
      <h3 id="satuan-judul" class="text-[19px] font-semibold tracking-[-0.025em] text-[#14111C]">Beli sesuai kebutuhan</h3>
      <p class="mt-1 text-[14.5px] leading-relaxed text-[#4B4757]">{{ rupiah(UNIT_PRICE) }} per token, minimal {{ UNIT_MIN }} token.</p>
    </div>
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div class="flex items-center justify-between gap-2 rounded-full bg-white/75 p-1 shadow-[0_4px_14px_-4px_rgba(20,17,28,0.08)] backdrop-blur-sm">
        <button type="button" :class="stepBtn" aria-label="Kurangi 5 token" @click="step(-5)">&minus;</button>
        <span class="min-w-[88px] text-center text-[18px] font-semibold tabular-nums text-[#14111C]" aria-live="polite">{{ count }} token</span>
        <button type="button" :class="stepBtn" aria-label="Tambah 5 token" @click="step(5)">+</button>
      </div>
      <button
        type="button"
        class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-7 text-[14.5px] font-semibold shadow-[0_10px_24px_-8px_rgba(17,14,24,0.38)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
        @click="emit('choose', { id: 'pkg_tokens', name: `${count} token satuan`, tokens: count, price: total, tokenAmount: count })"
      >Beli {{ rupiah(total) }}</button>
    </div>
  </section>
</template>
