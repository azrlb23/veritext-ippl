<script setup lang="ts">
// Temuan kunci sebagai tipografi besar dengan interaksi taktil halus.
const findings = [
  { value: "12", unit: "kalimat identik", text: "Penggalan yang sama persis dengan dokumen arsip internal 2023." },
  { value: "4", unit: "kalimat parafrasa", text: "Susunannya diubah, tetapi maknanya tetap sangat dekat dengan sumber." },
  { value: "0,9%", unit: "pola mesin", text: "Variasi panjang kalimat dan kosakata menunjukkan tulisan manusia." },
];
</script>

<template>
  <div class="grid gap-10 md:grid-cols-3 md:gap-6 lg:block lg:space-y-12">
    <div
      v-for="f in findings"
      :key="f.unit"
      class="group cursor-default rounded-[24px] p-2 transition-all duration-300 hover:bg-[#F3EEFA]/30"
    >
      <div class="flex items-baseline gap-3">
        <span class="text-[64px] font-semibold leading-none tracking-[-0.055em] text-[#14111C] md:text-[56px] lg:text-[76px] transition-transform duration-300 group-hover:scale-105 origin-left tabular-nums">
          {{ f.value }}
        </span>
        <span class="vt-accent text-[20px] leading-none">{{ f.unit }}</span>
      </div>
      <p class="mt-3 max-w-[300px] text-[15px] leading-[1.65] text-[#4B4757] transition-colors group-hover:text-[#14111C]">
        {{ f.text }}
      </p>
    </div>
  </div>
</template>
