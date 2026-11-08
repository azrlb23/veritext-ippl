<script setup lang="ts">
import { onMounted, ref } from "vue";

const displayScore = ref(0);
const activeMetric = ref<number | null>(null);

const metrics = [
  { label: "Kecocokan kata", value: 8, bar: "bg-[#EF4444]" },
  { label: "Kecocokan makna", value: 14, bar: "bg-[#F97316]" },
  { label: "Pola tulisan AI", value: 20, bar: "bg-[#EAB308]" },
];

function triggerScoreCount() {
  displayScore.value = 0;
  const target = 88;
  const duration = 1200;
  const start = performance.now();

  function step(now: number) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    displayScore.value = Math.round(ease * target);
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }
  requestAnimationFrame(step);
}

onMounted(() => {
  setTimeout(triggerScoreCount, 400);
});
</script>

<template>
  <div
    class="w-[292px] rounded-[26px] bg-white p-5 shadow-float origin-right [transform:perspective(1200px)_rotateY(24deg)_rotateZ(-5deg)] transition-all duration-500 ease-out hover:[transform:perspective(1200px)_rotateY(8deg)_rotateZ(-2deg)_translateY(-8px)] hover:shadow-2xl animate-card-left cursor-pointer"
    aria-hidden="true"
    @mouseenter="triggerScoreCount"
  >
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-[12px] bg-[#F3EEFA] flex items-center justify-center text-[#14111C] transition-transform duration-300 group-hover:scale-105">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6" />
        </svg>
      </div>
      <div class="min-w-0">
        <div class="text-[13px] font-semibold text-[#14111C] truncate">Naskah-Laporan.pdf</div>
        <div class="text-[11.5px] text-[#5E5A6B]">2.140 kata, 1 token</div>
      </div>
    </div>

    <div class="mt-5 flex items-end justify-between">
      <div>
        <div class="text-[46px] leading-none font-semibold tracking-[-0.04em] text-[#14111C] tabular-nums transition-all">
          {{ displayScore }}%
        </div>
        <div class="mt-1.5 text-[12px] text-[#5E5A6B]">Skor orisinalitas</div>
      </div>
      <svg class="h-14 w-14 -rotate-90" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#EFEAF6" stroke-width="3.6" />
        <circle
          cx="18"
          cy="18"
          r="15.9"
          fill="none"
          stroke="#8A3FE0"
          stroke-width="3.6"
          stroke-linecap="round"
          :stroke-dasharray="`${displayScore} 100`"
          class="transition-all duration-300"
        />
      </svg>
    </div>

    <div class="mt-5 space-y-3.5">
      <div
        v-for="(m, idx) in metrics"
        :key="m.label"
        class="transition-transform duration-200"
        :class="activeMetric === idx ? 'scale-[1.02]' : ''"
        @mouseenter.stop="activeMetric = idx"
        @mouseleave.stop="activeMetric = null"
      >
        <div class="flex items-center justify-between text-[12px]">
          <span class="text-[#4B4757]">{{ m.label }}</span>
          <span class="font-semibold text-[#14111C] tabular-nums">{{ m.value }}%</span>
        </div>
        <div class="mt-1.5 h-1.5 w-full rounded-full bg-[#EFEAF6] overflow-hidden">
          <div
            class="h-1.5 rounded-full transition-all duration-700 ease-out"
            :class="m.bar"
            :style="{ width: (displayScore > 0 ? m.value * 3 : 0) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <div class="mt-5 h-10 rounded-full bg-[#14111C] text-white text-[12.5px] font-semibold flex items-center justify-center shadow-btn-dark transition-all duration-200 hover:bg-[#2B2438] active:scale-[0.98]">
      Unduh sertifikat
    </div>
  </div>
</template>
