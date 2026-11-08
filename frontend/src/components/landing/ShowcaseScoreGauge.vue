<script setup lang="ts">
// Kartu skor ringkas yang menumpang di sudut kartu naskah.
</script>

<template>
  <div class="rounded-[28px] bg-white p-5 shadow-float">
    <div class="text-[12.5px] font-medium text-[#4B4757]">Skor orisinalitas</div>
    <div class="mt-1 flex items-center justify-between gap-4">
      <div class="text-[50px] font-semibold leading-none tracking-[-0.05em] text-[#14111C] tabular-nums">84,8%</div>
      <svg class="h-[60px] w-[60px] shrink-0 -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EFEAF6" stroke-width="3.6" />
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#8A3FE0" stroke-width="3.6" stroke-linecap="round" stroke-dasharray="84.8 100" />
      </svg>
    </div>
    <div class="mt-2 text-[12px] text-[#5E5A6B]">Di bawah batas aman 20% kesamaan</div>
  </div>
</template>
