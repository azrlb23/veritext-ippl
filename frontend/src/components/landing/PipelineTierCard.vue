<script setup lang="ts">
interface TierItem {
  id: number;
  tabLabel: string;
  title: string;
  description: string;
  weight: string;
  icon: string;
}

defineProps<{ tier: TierItem; isActive: boolean }>();
defineEmits<{ (e: "select"): void }>();

const icons: Record<string, string> = {
  doc: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  stack: "M4 7l8-4 8 4-8 4-8-4zM4 12l8 4 8-4M4 17l8 4 8-4",
  gauge: "M13 10V3L4 14h7v7l9-11h-7z",
};
</script>

<template>
  <div
    @click="$emit('select')"
    class="flex cursor-pointer flex-col justify-between rounded-[32px] p-8 transition-all duration-300 ease-out"
    :class="isActive
      ? 'bg-gradient-to-br from-[#1A73D9] to-[#5B5BEA] text-white shadow-[0_30px_60px_-20px_rgba(60,70,220,0.55)] md:-translate-y-3'
      : 'bg-white text-[#0B0F19] shadow-lift hover:-translate-y-1'"
  >
    <div>
      <div
        class="flex h-12 w-12 items-center justify-center rounded-[16px]"
        :class="isActive ? 'bg-white/20 text-white' : 'bg-[#F1F4FB] text-[#0B0F19]'"
      >
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" :d="icons[tier.icon]" />
        </svg>
      </div>

      <h3 class="mt-7 text-[26px] font-semibold leading-[1.15] tracking-[-0.03em]">{{ tier.title }}</h3>
      <p class="mt-3 text-[15px] leading-[1.65]" :class="isActive ? 'text-white/85' : 'text-[#4A5266]'">
        {{ tier.description }}
      </p>
    </div>

    <div class="mt-9 flex items-baseline gap-2">
      <span class="text-[34px] font-semibold tracking-[-0.04em] tabular-nums">{{ tier.weight }}</span>
      <span class="text-[13px]" :class="isActive ? 'text-white/80' : 'text-[#6B7385]'">dari skor akhir</span>
    </div>
  </div>
</template>
