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
      class="flex flex-col rounded-[32px] p-7 shadow-float"
      :class="p.featured ? 'bg-gradient-to-br from-[#8A3FE0] via-[#B478DF] to-[#D26BE6] text-white' : 'bg-white text-[#14111C]'"
    >
      <h3 class="text-[18px] font-semibold tracking-[-0.02em]">{{ p.name }}</h3>
      <p class="mt-5 text-[56px] font-semibold leading-none tracking-[-0.05em] tabular-nums">{{ p.tokens }}<span class="ml-2 text-[18px] font-medium tracking-normal opacity-80">token</span></p>
      <p class="mt-4 text-[15px] leading-relaxed" :class="p.featured ? 'text-white/90' : 'text-[#4B4757]'">{{ p.note }}</p>
      <p class="mt-auto pt-6 text-[26px] font-semibold tracking-[-0.03em] tabular-nums">{{ rupiah(p.price) }}</p>
      <p class="text-[13px]" :class="p.featured ? 'text-white/80' : 'text-[#5E5A6B]'">{{ perToken(p) }} per token</p>
      <button
        type="button"
        class="mt-5 inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full text-[15px] font-semibold transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
        :class="p.featured ? 'bg-[#14111C] text-white shadow-btn-dark' : 'bg-[#14111C] text-white shadow-btn-dark'"
        @click="$emit('choose', { id: p.id, name: `Paket ${p.name}`, tokens: p.tokens, price: p.price })"
      >Pilih {{ p.name }}</button>
    </article>
  </div>
</template>
