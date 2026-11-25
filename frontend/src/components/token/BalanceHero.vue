<script setup lang="ts">
defineProps<{ balance: number; role: string }>();
</script>

<template>
  <section class="border-b border-[#E6ECEB] pb-8" aria-label="Saldo token">
    <div>
      <p class="text-[13.5px] font-medium text-[#5E5A6B]">Saldo Anda</p>
      <p class="mt-1.5 text-[72px] font-semibold leading-none tracking-[-0.06em] text-[#14111C] tabular-nums sm:text-[96px]">
        {{ balance }}<span class="ml-3 text-[28px] font-medium tracking-[-0.04em] text-[#0F766E] sm:text-[36px]">token</span>
      </p>
      <p class="mt-2.5 text-[14.5px] text-[#5E5A6B]">Paket {{ role === "PREMIUM" ? "Premium" : "Gratis" }}</p>
    </div>
  </section>
</template>
