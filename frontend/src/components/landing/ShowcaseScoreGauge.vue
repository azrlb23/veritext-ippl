<script setup lang="ts">
const rows = [
  { label: "Kecocokan kata", note: "bobot 50%", value: "10,5%", bar: "bg-[#EF4444]", width: "52%" },
  { label: "Kecocokan makna", note: "bobot 35%", value: "3,8%", bar: "bg-[#F97316]", width: "19%" },
  { label: "Pola tulisan AI", note: "bobot 15%", value: "0,9%", bar: "bg-[#EAB308]", width: "5%" },
];
</script>

<template>
  <div class="lg:col-span-5 rounded-[28px] bg-white p-6 shadow-lift sm:p-8">
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[13px] font-medium text-[#4A5266]">Skor orisinalitas</div>
        <div class="mt-1 text-[52px] font-semibold leading-none tracking-[-0.045em] text-[#0B0F19] tabular-nums">84,8%</div>
        <div class="mt-2 text-[12.5px] text-[#6B7385]">Di bawah batas aman 20% kesamaan</div>
      </div>
      <svg class="h-20 w-20 -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EEF1F8" stroke-width="3.4" />
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#1A73D9" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="84.8 100" />
      </svg>
    </div>

    <div class="mt-7 space-y-4">
      <div v-for="r in rows" :key="r.label">
        <div class="flex items-baseline justify-between text-[13.5px]">
          <span class="font-medium text-[#0B0F19]">{{ r.label }} <span class="text-[12px] font-normal text-[#6B7385]">{{ r.note }}</span></span>
          <span class="font-semibold text-[#0B0F19] tabular-nums">{{ r.value }}</span>
        </div>
        <div class="mt-2 h-1.5 w-full rounded-full bg-[#EEF1F8]">
          <div class="h-1.5 rounded-full" :class="r.bar" :style="{ width: r.width }"></div>
        </div>
      </div>
    </div>

    <div class="mt-6 flex items-center justify-between rounded-[16px] bg-[#F6F7FB] px-4 py-3 text-[13.5px]">
      <span class="text-[#4A5266]">Kesamaan komposit</span>
      <span class="font-semibold text-[#0B0F19] tabular-nums">15,2%</span>
    </div>
  </div>
</template>
