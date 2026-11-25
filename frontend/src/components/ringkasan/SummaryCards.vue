<script setup lang="ts">
defineProps<{
  balance: number;
  total: number;
  done: number;
  average: number | null;
  role?: string;
  asistenTo?: string;
}>();
</script>

<template>
  <div class="grid gap-8 border-b border-[#E6ECEB] pb-8 lg:grid-cols-[1.15fr_1fr] lg:gap-10">
    <section class="vt-reveal flex flex-col justify-between" aria-label="Saldo token">
      <div>
        <div class="flex items-center gap-3">
          <p class="text-[13.5px] font-medium text-[#5E5A6B]">Saldo token</p>
          <span class="text-[12.5px] font-semibold text-[#0F766E]">
            Paket {{ (role || "FREE").toUpperCase() === "PREMIUM" ? "Premium" : "Gratis" }}
          </span>
        </div>
        <p class="mt-1.5 text-[68px] font-semibold leading-none tracking-[-0.06em] tabular-nums text-[#14111C] sm:text-[84px]">
          {{ balance }}<span class="ml-2.5 text-[24px] font-medium tracking-[-0.03em] text-[#0F766E] sm:text-[30px]">token</span>
        </p>
      </div>
      <div class="mt-6 flex flex-wrap items-center gap-3">
        <router-link
          to="/periksa"
          class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-7 text-[14.5px] font-semibold shadow-[0_10px_24px_-8px_rgba(17,14,24,0.38)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
        >Periksa naskah</router-link>
        <router-link
          to="/billing"
          class="vt-btn-light inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        >Tambah token</router-link>
      </div>
    </section>

    <section class="vt-reveal vt-d-1 flex flex-col justify-between border-t border-[#E6ECEB] pt-6 lg:border-l lg:border-t-0 lg:pl-10 lg:pt-0" aria-label="Ringkasan angka">
      <div class="grid grid-cols-3 gap-4">
        <div>
          <p class="text-[36px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[42px]">{{ total }}</p>
          <p class="mt-2 text-[13.5px] text-[#5E5A6B]">pemeriksaan</p>
        </div>
        <div>
          <p class="text-[36px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[42px]">{{ done }}</p>
          <p class="mt-2 text-[13.5px] text-[#5E5A6B]">selesai</p>
        </div>
        <div>
          <p class="text-[36px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C] sm:text-[42px]">{{ average === null ? "-" : average.toFixed(0) + "%" }}</p>
          <p class="mt-2 text-[13.5px] text-[#5E5A6B]">rata-rata kemiripan</p>
        </div>
      </div>

      <div class="mt-6 flex items-center justify-between gap-3 pt-2">
        <span class="text-[13px] text-[#5E5A6B]">Butuh bantuan perbaikan kalimat?</span>
        <router-link
          :to="asistenTo || '/asisten'"
          class="vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-5 text-[13.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        >Buka Asisten AI &rarr;</router-link>
      </div>
    </section>
  </div>
</template>
