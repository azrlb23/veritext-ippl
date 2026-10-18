<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  score: number;
  label?: string;
  size?: "sm" | "md" | "lg";
}>();

const severityLevel = computed(() => {
  const val = props.score;
  if (val <= 25) {
    return {
      category: "Aman",
      textColor: "text-[#065f46]",
      bgColor: "bg-audyr-mint-whisper",
      borderColor: "border-[#a7f3d0]",
      strokeColor: "#10b981",
    };
  } else if (val <= 50) {
    return {
      category: "Perlu Perhatian",
      textColor: "text-yellow-700",
      bgColor: "bg-yellow-50",
      borderColor: "border-yellow-300",
      strokeColor: "#EAB308",
    };
  } else if (val <= 75) {
    return {
      category: "Terindikasi Plagiarisme",
      textColor: "text-orange-700",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-300",
      strokeColor: "#F97316",
    };
  } else {
    return {
      category: "Plagiarisme Berat",
      textColor: "text-red-700",
      bgColor: "bg-red-50",
      borderColor: "border-red-300",
      strokeColor: "#EF4444",
    };
  }
});
</script>

<template>
  <div class="inline-flex flex-col items-center justify-center p-5 rounded-[14px] bg-white border border-[#ededed] shadow-audyr-subtle">
    <div class="relative flex items-center justify-center w-28 h-28">
      <!-- Circular Ring Mockup -->
      <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
        <path
          class="text-[#ededed]"
          stroke-width="3.5"
          stroke="currentColor"
          fill="none"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
        />
        <path
          :stroke="severityLevel.strokeColor"
          :stroke-dasharray="`${score}, 100`"
          stroke-linecap="round"
          stroke-width="3.5"
          fill="none"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
        />
      </svg>
      <div class="absolute flex flex-col items-center">
        <span class="text-2xl font-bold tracking-tight font-mono text-audyr-ink">
          {{ score.toFixed(1) }}%
        </span>
        <span class="text-[10px] text-audyr-ash font-medium tracking-tight">SIMILARITY</span>
      </div>
    </div>

    <div
      class="mt-3 px-3 py-0.5 rounded-full text-xs font-medium border tracking-tight"
      :class="[severityLevel.textColor, severityLevel.bgColor, severityLevel.borderColor]"
    >
      {{ severityLevel.category }}
    </div>
  </div>
</template>
