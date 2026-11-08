<script setup lang="ts">
// Tiga kartu metrik kecil yang disusun bertumpuk dengan kemiringan berbeda.
const items = [
  { label: "Kecocokan kata", value: "10,5%", width: "52%", bar: "bg-[#EF4444]", tilt: "lg:-rotate-3 lg:translate-y-2" },
  { label: "Kecocokan makna", value: "3,8%", width: "19%", bar: "bg-[#F97316]", tilt: "lg:rotate-2 lg:-translate-y-3" },
  { label: "Pola tulisan AI", value: "0,9%", width: "5%", bar: "bg-[#EAB308]", tilt: "lg:-rotate-2 lg:translate-y-1" },
];
</script>

<template>
  <div class="flex items-end gap-3">
    <div v-for="m in items" :key="m.label" class="flex-1 rounded-[22px] bg-white p-4 shadow-lift lg:w-[168px] lg:flex-none" :class="m.tilt">
      <div class="text-[12px] text-[#5E5A6B]">{{ m.label }}</div>
      <div class="mt-1 text-[26px] font-semibold tracking-[-0.03em] text-[#14111C] tabular-nums">{{ m.value }}</div>
      <div class="mt-3 h-1.5 w-full rounded-full bg-[#EFEAF6]">
        <div class="h-1.5 rounded-full" :class="m.bar" :style="{ width: m.width }"></div>
      </div>
    </div>
  </div>
</template>
