<script setup lang="ts">
// Temuan kunci sebagai tipografi besar, bukan kotak.
const findings = [
  { value: "12", unit: "kalimat identik", text: "Penggalan yang sama persis dengan dokumen arsip internal 2023." },
  { value: "4", unit: "kalimat parafrasa", text: "Susunannya diubah, tetapi maknanya tetap sangat dekat dengan sumber." },
  { value: "0,9%", unit: "pola mesin", text: "Variasi panjang kalimat dan kosakata menunjukkan tulisan manusia." },
];
</script>

<template>
  <div class="space-y-10 lg:space-y-14">
    <div v-for="f in findings" :key="f.unit">
      <div class="flex items-baseline gap-3">
        <span class="text-[64px] font-semibold leading-none tracking-[-0.055em] text-[#14111C] sm:text-[80px]">{{ f.value }}</span>
        <span class="vt-accent text-[20px] leading-none">{{ f.unit }}</span>
      </div>
      <p class="mt-3 max-w-[300px] text-[15px] leading-[1.65] text-[#4B4757]">{{ f.text }}</p>
    </div>
  </div>
</template>
