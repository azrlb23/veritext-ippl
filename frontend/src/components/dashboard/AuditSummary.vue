<script setup lang="ts">
import type { DocumentEstimate } from "../../services/documentService";

const props = defineProps<{
  balance: number;
  fileName: string;
  estimate: DocumentEstimate | null;
  isEstimating: boolean;
  estimateError: string;
  needsConsent: boolean;
  consent: boolean;
  isReady: boolean;
  isUploading: boolean;
}>();
const emit = defineEmits<{ (e: "update:consent", value: boolean): void; (e: "start"): void; (e: "topup"): void }>();

const cost = () => (props.estimate ? props.estimate.token_cost : null);
const remaining = () => (cost() === null ? null : Math.max(0, props.balance - (cost() as number)));
const insufficient = () => cost() !== null && props.balance < (cost() as number);
const overPlan = () => props.estimate !== null && !props.estimate.within_plan;
const words = () => (props.estimate ? props.estimate.word_count.toLocaleString("id-ID") : "-");
</script>

<template>
  <div class="rounded-[32px] bg-white p-7 shadow-float lg:sticky lg:top-28">
    <div class="text-[14px] font-medium text-[#5E5A6B]">Ringkasan</div>
    <p class="mt-1 truncate text-[16px] font-semibold text-[#14111C]">{{ fileName || "Belum ada naskah dipilih" }}</p>

    <dl class="mt-6 space-y-3.5 text-[14.5px]">
      <div class="flex items-center justify-between">
        <dt class="text-[#4B4757]">Jumlah kata</dt>
        <dd class="font-semibold tabular-nums text-[#14111C]">{{ isEstimating ? "Menghitung..." : words() }}</dd>
      </div>
      <div class="flex items-center justify-between">
        <dt class="text-[#4B4757]">Saldo token</dt>
        <dd class="font-semibold tabular-nums text-[#14111C]">{{ balance }}</dd>
      </div>
      <div class="flex items-center justify-between">
        <dt class="text-[#4B4757]">Biaya pemeriksaan</dt>
        <dd class="font-semibold tabular-nums text-[#14111C]">{{ cost() === null ? "-" : "-" + cost() }}</dd>
      </div>
    </dl>

    <div class="mt-5 rounded-[20px] bg-[#F3EEFA] px-5 py-4">
      <div class="text-[12.5px] text-[#5E5A6B]">Saldo setelah pemeriksaan</div>
      <div class="mt-1 text-[34px] font-semibold leading-none tracking-[-0.04em] tabular-nums" :class="insufficient() ? 'text-[#B91C1C]' : 'text-[#14111C]'">
        {{ remaining() === null ? "-" : remaining() }} <span class="text-[15px] font-medium tracking-normal text-[#5E5A6B]">token</span>
      </div>
      <p class="mt-2 text-[12.5px] leading-[1.5] text-[#5E5A6B]">1 token untuk tiap 2.500 kata, maksimal 5 token per naskah.</p>
    </div>

    <p v-if="estimateError" role="alert" class="mt-4 text-[14px] leading-[1.6] text-[#B91C1C]">{{ estimateError }}</p>
    <p v-else-if="overPlan()" role="alert" class="mt-4 text-[14px] leading-[1.6] text-[#B91C1C]">
      Akun FREE dibatasi {{ estimate?.max_free_words.toLocaleString("id-ID") }} kata per naskah.
      <button type="button" class="cursor-pointer font-semibold underline" @click="emit('topup')">Lihat paket Premium</button>
    </p>
    <p v-else-if="insufficient()" role="alert" class="mt-4 text-[14px] leading-[1.6] text-[#B91C1C]">
      Saldo tidak cukup.
      <button type="button" class="cursor-pointer font-semibold underline" @click="emit('topup')">Isi token</button>
    </p>

    <label v-if="needsConsent" class="mt-4 flex min-h-[44px] cursor-pointer select-none items-center gap-2.5 text-[13.5px] leading-tight text-[#4B4757]">
      <input type="checkbox" class="h-[18px] w-[18px] shrink-0 rounded accent-[#8A3FE0]" :checked="consent" @change="emit('update:consent', ($event.target as HTMLInputElement).checked)" />
      <span>Setujui pemrosesan teks naskah untuk evaluasi AI.</span>
    </label>

    <button
      type="button"
      :disabled="!isReady"
      class="mt-5 flex h-[54px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:bg-[#D9D3E4] disabled:text-[#5E5A6B] disabled:shadow-none disabled:hover:translate-y-0"
      @click="emit('start')"
    >
      {{ isUploading ? "Mengunggah ke antrean..." : "Mulai periksa" }}
    </button>
  </div>
</template>
