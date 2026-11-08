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
    class="group flex cursor-pointer flex-col justify-between rounded-[32px] p-8 transition-all duration-500 ease-out relative overflow-hidden"
    :class="isActive
      ? 'bg-gradient-to-br from-[#7A2FD6] to-[#9B4FE6] text-white shadow-[0_32px_64px_-16px_rgba(122,47,214,0.45)] md:-translate-y-4 scale-[1.02]'
      : 'bg-white text-[#14111C] shadow-lift hover:-translate-y-2 hover:shadow-float hover:scale-[1.01]'"
  >
    <div
      v-if="isActive"
      class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10 blur-2xl"
      aria-hidden="true"
    />

    <div>
      <div class="flex items-center justify-between">
        <div
          class="flex h-12 w-12 items-center justify-center rounded-[16px] transition-transform duration-300 group-hover:scale-110"
          :class="isActive ? 'bg-white/20 text-white shadow-[0_0_20px_rgba(255,255,255,0.25)]' : 'bg-[#F3EEFA] text-[#14111C]'"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" :d="icons[tier.icon]" />
          </svg>
        </div>
        <span
          v-if="isActive"
          class="rounded-full bg-white/20 px-3 py-1 text-[11.5px] font-medium text-white backdrop-blur-sm"
        >
          Lapis {{ tier.id + 1 }}
        </span>
      </div>

      <h3 class="mt-7 text-[26px] font-semibold leading-[1.15] tracking-[-0.03em]">{{ tier.title }}</h3>
      <p class="mt-3 text-[15px] leading-[1.65]" :class="isActive ? 'text-white/85' : 'text-[#4B4757]'">
        {{ tier.description }}
      </p>
    </div>

    <div class="mt-9 flex items-baseline gap-2">
      <span class="text-[34px] font-semibold tracking-[-0.04em] tabular-nums transition-transform duration-300 group-hover:scale-105 origin-left">{{ tier.weight }}</span>
      <span class="text-[13px]" :class="isActive ? 'text-white/80' : 'text-[#5E5A6B]'">dari skor akhir</span>
    </div>
  </div>
</template>
