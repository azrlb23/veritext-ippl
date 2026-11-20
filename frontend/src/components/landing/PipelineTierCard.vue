<script setup lang="ts">
import { computed } from "vue";
import { VtIcon, type VtIconName } from "../common";
import PipelineWaveArtwork from "./PipelineWaveArtwork.vue";

export interface TierItem {
  id: number;
  shortTitle: string;
  title: string;
  description: string;
  weight: string;
  icon: VtIconName;
}

const props = defineProps<{ tier: TierItem; isActive: boolean }>();
defineEmits<{ (e: "select"): void }>();

const stepNumber = computed(() => `${String(props.tier.id + 1).padStart(2, "0")}.`);
</script>

<template>
  <button
    type="button"
    @click="$emit('select')"
    :aria-pressed="isActive"
    class="group w-full cursor-pointer text-left transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
    :class="isActive
      ? 'md:flex-[1.95] md:h-[460px] rounded-[22px] border border-[#E6DDF7] bg-white p-5 sm:p-6 shadow-[0_28px_64px_-20px_rgba(122,47,214,0.18)] flex flex-col justify-between'
      : 'md:flex-[0.88] md:h-[360px] rounded-[20px] border border-[#ECE8F4] bg-white p-6 shadow-[0_12px_32px_-16px_rgba(20,17,28,0.08)] flex flex-col justify-between hover:-translate-y-1 hover:border-[#DDD0F7] hover:shadow-float'"
  >
    <PipelineWaveArtwork v-if="isActive" :tier-id="tier.id" />
    <span
      v-else
      class="text-[42px] font-light leading-none tracking-[-0.04em] text-[#E6E2EE] transition-colors group-hover:text-[#CFC3EA]"
    >
      {{ stepNumber }}
    </span>

    <div v-if="isActive" class="mt-6">
      <div class="flex items-center gap-2.5">
        <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#F5F2FA] text-[#7A2FD6]">
          <VtIcon :name="tier.icon" tone="violet" class="h-4 w-4" />
        </span>
        <span class="rounded-full bg-[#F5F2FA] px-2.5 py-1 text-[11px] font-semibold tracking-wide text-[#7A2FD6]">
          {{ tier.weight }}
        </span>
      </div>
      <h3 class="mt-4 text-[24px] font-medium leading-[1.15] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        {{ tier.title }}
      </h3>
      <p class="mt-3 text-[13.5px] leading-[1.6] text-[#5E5A6B]">
        {{ tier.description }}
      </p>
    </div>

    <div v-else class="mt-8">
      <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#F5F2FA] text-[#7A2FD6]">
        <VtIcon :name="tier.icon" tone="violet" class="h-4 w-4" />
      </span>
      <h3 class="mt-4 text-[15px] font-medium leading-[1.3] text-[#14111C]">
        {{ tier.shortTitle }}
      </h3>
    </div>
  </button>
</template>
