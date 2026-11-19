<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{ active?: boolean }>();
const displayScore = ref("0,0");
const dashOffset = ref(0);
let timerId: ReturnType<typeof setTimeout> | null = null;
let rafId: number | null = null;

function clearTimers() {
  if (timerId !== null) { clearTimeout(timerId); timerId = null; }
  if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null; }
}

function animateScore() {
  clearTimers();
  const target = 84.8, duration = 1200, start = performance.now();
  const step = (now: number) => {
    const p = Math.min((now - start) / duration, 1);
    const val = (1 - Math.pow(1 - p, 3)) * target;
    displayScore.value = val.toFixed(1).replace(".", ",");
    dashOffset.value = val;
    rafId = p < 1 ? requestAnimationFrame(step) : null;
  };
  rafId = requestAnimationFrame(step);
}

watch(() => props.active, (active) => {
  clearTimers();
  if (active) timerId = setTimeout(animateScore, 220);
  else if (active === false) { displayScore.value = "0,0"; dashOffset.value = 0; }
});
onMounted(() => {
  if (props.active === undefined) timerId = setTimeout(animateScore, 500);
  else if (props.active) timerId = setTimeout(animateScore, 220);
});
onBeforeUnmount(clearTimers);
</script>

<template>
  <div class="rounded-[28px] bg-white p-5 shadow-float transition-all duration-500 ease-out hover:rotate-0 hover:scale-105 hover:shadow-2xl cursor-pointer" @mouseenter="animateScore">
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
