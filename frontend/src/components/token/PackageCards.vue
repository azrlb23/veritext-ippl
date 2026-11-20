<script setup lang="ts">
import { PACKAGES, rupiah, type PurchaseTarget } from "../../composables/useTokenPurchase";

defineEmits<{ (e: "choose", t: PurchaseTarget): void }>();
const perToken = (p: { price: number; tokens: number }) => rupiah(Math.round(p.price / p.tokens));
</script>

<template>
  <div class="grid gap-5 md:grid-cols-3">
    <article
      v-for="p in PACKAGES"
      :key="p.id"
      class="flex flex-col rounded-[32px] border p-7 shadow-float"
      :class="p.featured ? 'border-[#CBE6E1] bg-[#EBF8F6] text-[#14111C]' : 'border-[#E8ECEB] bg-white text-[#14111C]'"
    >
      <h3 class="text-[18px] font-semibold tracking-[-0.02em]" :class="p.featured ? 'text-[#0F766E]' : 'text-[#14111C]'">{{ p.name }}</h3>
      <p class="mt-5 text-[56px] font-semibold leading-none tracking-[-0.05em] tabular-nums">{{ p.tokens }}<span class="ml-2 text-[18px] font-medium tracking-normal" :class="p.featured ? 'text-[#0F766E]' : 'text-[#5E5A6B]'">token</span></p>
      <p class="mt-4 text-[15px] leading-relaxed text-[#4B4757]">{{ p.note }}</p>
      <p class="mt-auto pt-6 text-[26px] font-semibold tracking-[-0.03em] tabular-nums">{{ rupiah(p.price) }}</p>
      <p class="text-[13px] text-[#5E5A6B]">{{ perToken(p) }} per token</p>
      <button
        type="button"
        class="vt-btn-dark mt-5 inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
        @click="$emit('choose', { id: p.id, name: `Paket ${p.name}`, tokens: p.tokens, price: p.price })"
      >Pilih {{ p.name }}</button>
    </article>
  </div>
</template>
