<script setup lang="ts">
// Ilustrasi layar ponsel yang menampilkan hasil verifikasi. Data contoh.
const bars = [
  { label: "Kata", value: "8%", width: "8%", bar: "bg-[#EF4444]" },
  { label: "Makna", value: "14%", width: "14%", bar: "bg-[#F97316]" },
  { label: "Pola AI", value: "20%", width: "20%", bar: "bg-[#EAB308]" },
];
</script>

<template>
  <div
    class="w-[228px] rotate-2 rounded-[40px] bg-[#14111C] p-[7px] shadow-float lg:[transform:perspective(1200px)_rotateY(-14deg)_rotateZ(3deg)]"
    aria-hidden="true"
  >
    <div class="rounded-[34px] bg-[#F7F4FB] px-4 pb-5 pt-3">
      <div class="mx-auto h-[5px] w-[52px] rounded-full bg-[#14111C]"></div>

      <div class="mt-5 flex items-center gap-1.5 text-[11.5px] font-semibold text-[#15803D]">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        Sertifikat terverifikasi
      </div>

      <div class="mt-4 flex items-center justify-between">
        <div>
          <div class="text-[40px] font-semibold leading-none tracking-[-0.05em] text-[#14111C]">88%</div>
          <div class="mt-1 text-[11px] text-[#5E5A6B]">Skor orisinalitas</div>
        </div>
        <svg class="h-[54px] w-[54px] -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EFEAF6" stroke-width="3.6" />
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#8A3FE0" stroke-width="3.6" stroke-linecap="round" stroke-dasharray="88 100" />
        </svg>
      </div>

      <div class="mt-4 space-y-3 rounded-[20px] bg-white p-3.5 shadow-lift">
        <div v-for="b in bars" :key="b.label">
          <div class="flex items-baseline justify-between text-[10.5px]">
            <span class="text-[#4B4757]">{{ b.label }}</span>
            <span class="font-semibold text-[#14111C]">{{ b.value }}</span>
          </div>
          <div class="mt-1 h-1 w-full rounded-full bg-[#EFEAF6]"><div class="h-1 rounded-full" :class="b.bar" :style="{ width: b.width }"></div></div>
        </div>
      </div>

      <div class="mt-4 flex h-9 items-center justify-center rounded-full bg-[#14111C] text-[11.5px] font-semibold text-white">Bagikan tautan</div>
    </div>
  </div>
</template>
