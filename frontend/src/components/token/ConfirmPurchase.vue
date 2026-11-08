<script setup lang="ts">
import { rupiah, type PurchaseTarget } from "../../composables/useTokenPurchase";

defineProps<{ target: PurchaseTarget | null; processing: boolean }>();
defineEmits<{ (e: "close"): void; (e: "confirm"): void }>();
</script>

<template>
  <div v-if="target" class="fixed inset-0 z-[60] flex items-end justify-center bg-[#14111C]/20 p-4 backdrop-blur-[2px] sm:items-center" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <div class="w-full max-w-md rounded-[32px] bg-white p-7 shadow-float" role="dialog" aria-modal="true" aria-labelledby="beli-judul">
      <h2 id="beli-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Konfirmasi pembelian</h2>
      <dl class="mt-5 space-y-3 rounded-[24px] bg-[#F3EEFA] p-5 text-[15px]">
        <div class="flex justify-between gap-4"><dt class="text-[#5E5A6B]">Pilihan</dt><dd class="text-right font-semibold text-[#14111C]">{{ target.name }}</dd></div>
        <div class="flex justify-between gap-4"><dt class="text-[#5E5A6B]">Token</dt><dd class="font-semibold tabular-nums text-[#14111C]">{{ target.tokens }}</dd></div>
        <div class="flex justify-between gap-4"><dt class="text-[#5E5A6B]">Total</dt><dd class="text-[18px] font-semibold tabular-nums text-[#14111C]">{{ rupiah(target.price) }}</dd></div>
      </dl>
      <p class="mt-4 text-[14px] leading-relaxed text-[#5E5A6B]">Anda memilih metode bayar di langkah berikutnya. Token masuk otomatis setelah pembayaran berhasil.</p>
      <div class="mt-7 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <button type="button" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-white px-6 text-[15px] font-semibold text-[#14111C] shadow-lift" @click="$emit('close')">Batal</button>
        <button type="button" :disabled="processing" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark disabled:opacity-40" @click="$emit('confirm')">{{ processing ? "Memproses..." : "Lanjut ke pembayaran" }}</button>
      </div>
    </div>
  </div>
</template>
