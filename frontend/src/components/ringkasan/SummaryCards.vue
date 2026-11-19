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
  <div class="grid gap-5 lg:grid-cols-[1.1fr_1fr]">
    <section class="vt-reveal flex flex-col justify-between rounded-[36px] bg-white p-7 shadow-float sm:p-9" aria-label="Saldo token">
      <div>
        <p class="text-[14px] font-medium text-[#5E5A6B]">Saldo token</p>
        <p class="mt-2 text-[80px] font-semibold leading-none tracking-[-0.06em] tabular-nums text-[#14111C]">{{ balance }}</p>
      </div>
      <div class="mt-8 flex flex-col gap-3 sm:flex-row">
        <router-link
          to="/periksa"
          class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
        >Periksa naskah</router-link>
        <router-link
          to="/billing"
          class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#F3EEFA] px-8 text-[15px] font-semibold text-[#14111C] transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        >Tambah token</router-link>
      </div>
    </section>

    <section class="vt-reveal vt-d-1 flex flex-col justify-between rounded-[36px] bg-[#F3EEFA] p-7 shadow-float sm:p-9" aria-label="Ringkasan angka">
      <div class="grid grid-cols-3 gap-3">
        <div>
          <p class="text-[44px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C]">{{ total }}</p>
          <p class="mt-2 text-[14px] text-[#5E5A6B]">pemeriksaan</p>
        </div>
        <div>
          <p class="text-[44px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C]">{{ done }}</p>
          <p class="mt-2 text-[14px] text-[#5E5A6B]">selesai</p>
        </div>
        <div>
          <p class="text-[44px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#14111C]">{{ average === null ? "-" : average.toFixed(0) + "%" }}</p>
          <p class="mt-2 text-[14px] text-[#5E5A6B]">rata-rata kemiripan</p>
        </div>
      </div>

      <div class="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-[#14111C]/[0.07] pt-5">
        <span class="rounded-full bg-white px-3.5 py-1.5 text-[12.5px] font-semibold text-[#6D28D9]">
          Paket {{ (role || "FREE").toUpperCase() === "PREMIUM" ? "Premium" : "Gratis" }}
        </span>
        <router-link
          :to="asistenTo || '/asisten'"
          class="inline-flex h-10 cursor-pointer items-center rounded-full bg-white px-5 text-[13.5px] font-semibold text-[#14111C] shadow-lift transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        >Buka Asisten AI &rarr;</router-link>
      </div>
    </section>
  </div>
</template>
