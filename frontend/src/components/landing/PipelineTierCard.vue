<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

interface TierItem {
  id: number;
  tabLabel: string;
  title: string;
  description: string;
  weight: string;
  icon: VtIconName;
}

defineProps<{ tier: TierItem; isActive: boolean }>();
defineEmits<{ (e: "select"): void }>();
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
        <VtIcon :name="tier.icon" :tone="isActive ? 'current' : 'violet'" class="h-8 w-8 shrink-0 transition-transform duration-300 group-hover:scale-110" :class="isActive ? 'text-white' : 'text-[#14111C]'" />
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
