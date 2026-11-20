<script setup lang="ts">
import { onMounted, ref, watch } from "vue";

const props = defineProps<{ active?: boolean }>();
const displayScore = ref(0);
const activeMetric = ref<number | null>(null);
let rafId: number | null = null;

const metrics = [
  { label: "Kecocokan kata", value: 8, bar: "bg-[#EF4444]" },
  { label: "Kecocokan makna", value: 14, bar: "bg-[#F97316]" },
  { label: "Pola tulisan AI", value: 20, bar: "bg-[#EAB308]" },
];

function triggerScoreCount() {
  if (rafId !== null) cancelAnimationFrame(rafId);
  displayScore.value = 0;
  const target = 88, duration = 1200, start = performance.now();
  const step = (now: number) => {
    const p = Math.min((now - start) / duration, 1);
    displayScore.value = Math.round((1 - Math.pow(1 - p, 3)) * target);
    rafId = p < 1 ? requestAnimationFrame(step) : null;
  };
  rafId = requestAnimationFrame(step);
}

watch(() => props.active, (active) => {
  if (active) triggerScoreCount();
  else if (active === false) {
    if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null; }
    displayScore.value = 0;
  }
});

onMounted(() => {
  if (props.active === undefined) setTimeout(triggerScoreCount, 400);
  else if (props.active) triggerScoreCount();
});
</script>

<template>
  <div
    class="w-[292px] rounded-[26px] bg-white p-5 shadow-float origin-right [transform:perspective(1200px)_rotateY(24deg)_rotateZ(-5deg)] transition-all duration-500 ease-out hover:[transform:perspective(1200px)_rotateY(8deg)_rotateZ(-2deg)_translateY(-8px)] hover:shadow-2xl animate-card-left cursor-pointer"
    aria-hidden="true"
    @mouseenter="triggerScoreCount"
  >
    <div class="min-w-0">
      <div class="text-[13px] font-semibold text-[#14111C] truncate">Naskah-Laporan.pdf</div>
      <div class="text-[11.5px] text-[#5E5A6B]">2.140 kata, 1 token</div>
    </div>

    <div class="mt-5 flex items-end justify-between">
      <div>
        <div class="text-[46px] leading-none font-semibold tracking-[-0.04em] text-[#14111C] tabular-nums transition-all">
          {{ displayScore }}%
        </div>
        <div class="mt-1.5 text-[12px] text-[#5E5A6B]">Skor orisinalitas</div>
      </div>
      <svg class="h-14 w-14 -rotate-90" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#E6F2F0" stroke-width="3.6" />
        <circle
          cx="18"
          cy="18"
          r="15.9"
          fill="none"
          stroke="#0F766E"
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
        <div class="mt-1.5 h-1.5 w-full rounded-full bg-[#E6F2F0] overflow-hidden">
          <div
            class="h-1.5 rounded-full transition-all duration-700 ease-out"
            :class="m.bar"
            :style="{ width: (displayScore > 0 ? m.value * 3 : 0) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <a
      href="/Laporan-Sampel-VeriText-AI.pdf"
      download="Laporan-Sampel-VeriText-AI.pdf"
      class="mt-5 flex h-10 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] text-[12.5px] font-semibold text-white shadow-btn-dark transition-all duration-200 hover:bg-[#2B2438] active:scale-[0.98]"
      @click.stop
    >
      Unduh sertifikat
    </a>
  </div>
</template>
