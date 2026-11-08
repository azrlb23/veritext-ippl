<script setup lang="ts">
defineProps<{ balance: number; role: string }>();
</script>

<template>
  <section class="rounded-[36px] bg-white p-7 shadow-float sm:p-10" aria-label="Saldo token">
    <div class="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-[14px] font-medium text-[#5E5A6B]">Saldo Anda</p>
        <p class="mt-2 text-[88px] font-semibold leading-none tracking-[-0.06em] text-[#14111C] tabular-nums sm:text-[120px]">
          {{ balance }}<span class="vt-accent ml-3 text-[36px] tracking-[-0.04em] sm:text-[44px]">token</span>
        </p>
        <p class="mt-3 text-[15px] text-[#5E5A6B]">Paket {{ role === "PREMIUM" ? "Premium" : "Gratis" }}</p>
      </div>
      <ul class="grid gap-3 rounded-[28px] bg-[#F3EEFA] p-6 text-[15px] leading-relaxed text-[#4B4757] lg:max-w-sm">
        <li><span class="font-semibold text-[#14111C]">1 token</span> memeriksa naskah hingga 2.500 kata.</li>
        <li><span class="font-semibold text-[#14111C]">Naskah panjang</span> dikenai satu token tambahan tiap 2.500 kata, maksimal 5 token.</li>
        <li><span class="font-semibold text-[#14111C]">Asisten AI:</span> 1 token untuk 10 pesan.</li>
      </ul>
    </div>
  </section>
</template>
