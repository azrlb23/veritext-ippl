<script setup lang="ts">
defineProps<{ balance: number; role: string }>();
</script>

<template>
  <section class="border-b border-[#E6ECEB] pb-8" aria-label="Saldo token">
    <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-[13.5px] font-medium text-[#5E5A6B]">Saldo Anda</p>
        <p class="mt-1.5 text-[72px] font-semibold leading-none tracking-[-0.06em] text-[#14111C] tabular-nums sm:text-[96px]">
          {{ balance }}<span class="ml-3 text-[28px] font-medium tracking-[-0.04em] text-[#0F766E] sm:text-[36px]">token</span>
        </p>
        <p class="mt-2.5 text-[14.5px] text-[#5E5A6B]">Paket {{ role === "PREMIUM" ? "Premium" : "Gratis" }}</p>
      </div>
      <ul class="grid gap-2.5 border-t border-[#E6ECEB] pt-5 text-[14.5px] leading-relaxed text-[#4B4757] lg:max-w-sm lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
        <li><span class="font-semibold text-[#0F766E]">1 token</span> memeriksa naskah hingga <span class="font-semibold text-[#14111C]">2.500 kata</span>.</li>
        <li><span class="font-semibold text-[#14111C]">Naskah panjang</span> dikenai satu token tambahan tiap 2.500 kata, <span class="font-semibold text-[#0F766E]">maksimal 5 token</span>.</li>
        <li><span class="font-semibold text-[#14111C]">Asisten AI:</span> <span class="font-semibold text-[#0F766E]">1 token untuk 10 pesan</span>.</li>
      </ul>
    </div>
  </section>
</template>
