<script setup lang="ts">
import { onMounted, ref } from "vue";

const displayScore = ref("0,0");
const dashOffset = ref(0);

function animateScore() {
  const target = 84.8;
  const duration = 1200;
  const start = performance.now();

  function step(now: number) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    displayScore.value = (ease * target).toFixed(1).replace(".", ",");
    dashOffset.value = ease * target;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

onMounted(() => {
  setTimeout(animateScore, 500);
});
</script>

<template>
  <div
    class="rounded-[28px] bg-white p-5 shadow-float transition-all duration-500 ease-out hover:rotate-0 hover:scale-105 hover:shadow-2xl cursor-pointer"
    @mouseenter="animateScore"
  >
    <div class="text-[12.5px] font-medium text-[#4B4757]">Skor orisinalitas</div>
    <div class="mt-1 flex items-center justify-between gap-4">
      <div class="text-[50px] font-semibold leading-none tracking-[-0.05em] text-[#14111C] tabular-nums">
        {{ displayScore }}%
      </div>
      <svg class="h-[60px] w-[60px] shrink-0 -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EFEAF6" stroke-width="3.6" />
        <circle
          cx="18"
          cy="18"
          r="15.9"
          fill="none"
          stroke="#8A3FE0"
          stroke-width="3.6"
          stroke-linecap="round"
          :stroke-dasharray="`${dashOffset} 100`"
          class="transition-all duration-300"
        />
      </svg>
    </div>
    <div class="mt-2 text-[12px] text-[#5E5A6B]">Di bawah batas aman 20% kesamaan</div>
  </div>
</template>
