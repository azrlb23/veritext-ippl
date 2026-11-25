<script setup lang="ts">
import { PACKAGES, rupiah, type PurchaseTarget } from "../../composables/useTokenPurchase";

defineEmits<{ (e: "choose", t: PurchaseTarget): void }>();
const perToken = (p: { price: number; tokens: number }) => rupiah(Math.round(p.price / p.tokens));
</script>

<template>
  <div class="grid gap-6 md:grid-cols-3 md:gap-4">
    <article
      v-for="p in PACKAGES"
      :key="p.id"
      class="flex flex-col rounded-2xl p-6 transition-colors duration-200 sm:p-7"
      :class="p.featured ? 'bg-[#EBF8F6]/70 backdrop-blur-sm' : 'bg-transparent'"
    >
      <div class="flex items-center justify-between gap-2">
        <h3 class="text-[17px] font-semibold tracking-[-0.02em]" :class="p.featured ? 'text-[#0F766E]' : 'text-[#14111C]'">
          {{ p.name }}
        </h3>
        <span v-if="p.featured" class="text-[12px] font-semibold text-[#0F766E]">Rekomendasi</span>
      </div>
      <p class="mt-4 text-[48px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[54px]">
        {{ p.tokens }}<span class="ml-2 text-[17px] font-medium tracking-normal" :class="p.featured ? 'text-[#0F766E]' : 'text-[#5E5A6B]'">token</span>
      </p>
      <p class="mt-3 text-[14.5px] leading-relaxed text-[#4B4757]">{{ p.note }}</p>
      <p class="mt-auto pt-6 text-[24px] font-semibold tracking-[-0.03em] tabular-nums text-[#14111C]">{{ rupiah(p.price) }}</p>
      <p class="text-[13px] text-[#5E5A6B]">{{ perToken(p) }} per token</p>
      <button
        type="button"
        class="mt-5 inline-flex h-11 w-full cursor-pointer items-center justify-center rounded-full text-[14.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
        :class="p.featured ? 'vt-btn-dark shadow-[0_10px_24px_-8px_rgba(17,14,24,0.38)]' : 'vt-btn-light'"
        @click="$emit('choose', { id: p.id, name: `Paket ${p.name}`, tokens: p.tokens, price: p.price })"
      >Pilih {{ p.name }}</button>
    </article>
  </div>
</template>
