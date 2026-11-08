<script setup lang="ts">
import { computed, ref } from "vue";
import { UNIT_MIN, UNIT_PRICE, rupiah, type PurchaseTarget } from "../../composables/useTokenPurchase";

const emit = defineEmits<{ (e: "choose", t: PurchaseTarget): void }>();
const count = ref(UNIT_MIN);
const total = computed(() => count.value * UNIT_PRICE);
const step = (d: number) => (count.value = Math.min(500, Math.max(UNIT_MIN, count.value + d)));
const stepBtn = "flex h-12 w-12 cursor-pointer items-center justify-center rounded-full bg-white text-[22px] font-semibold text-[#14111C] shadow-lift transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]";
</script>

<template>
  <section class="flex flex-col gap-6 rounded-[32px] bg-white p-7 shadow-float sm:p-9 lg:flex-row lg:items-center lg:justify-between" aria-labelledby="satuan-judul">
    <div class="max-w-md">
      <h3 id="satuan-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Beli sesuai kebutuhan</h3>
      <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">{{ rupiah(UNIT_PRICE) }} per token, minimal {{ UNIT_MIN }} token.</p>
    </div>
    <div class="flex flex-col gap-5 sm:flex-row sm:items-center">
      <div class="flex items-center justify-between gap-3 rounded-full bg-[#F3EEFA] p-1.5">
        <button type="button" :class="stepBtn" aria-label="Kurangi 5 token" @click="step(-5)">&minus;</button>
        <span class="min-w-[96px] text-center text-[22px] font-semibold tabular-nums text-[#14111C]" aria-live="polite">{{ count }} token</span>
        <button type="button" :class="stepBtn" aria-label="Tambah 5 token" @click="step(5)">+</button>
      </div>
      <button
        type="button"
        class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
        @click="emit('choose', { id: 'pkg_tokens', name: `${count} token satuan`, tokens: count, price: total, tokenAmount: count })"
      >Beli {{ rupiah(total) }}</button>
    </div>
  </section>
</template>
