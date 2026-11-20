<script setup lang="ts">
import { computed } from "vue";
import type { VtIconName } from "../common";
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
    @mouseenter="$emit('select')"
    @click="$emit('select')"
    :aria-pressed="isActive"
    class="group w-full cursor-pointer text-left transition-[flex-grow,transform,border-color] duration-300 ease-out"
    :class="isActive
      ? 'md:flex-[1.95] md:h-[460px] rounded-[22px] border border-[#D5ECE8] bg-white p-5 sm:p-6 shadow-[0_28px_64px_-20px_rgba(15,118,110,0.16)] flex flex-col justify-between'
      : 'md:flex-[0.88] md:h-[360px] rounded-[20px] border border-[#E8ECEB] bg-white p-6 shadow-[0_12px_32px_-16px_rgba(20,17,28,0.08)] flex flex-col justify-between hover:-translate-y-1 hover:border-[#CBE6E1] hover:shadow-float'"
  >
    <PipelineWaveArtwork v-if="isActive" :tier-id="tier.id" />
    <span
      v-else
      class="text-[42px] font-light leading-none tracking-[-0.04em] text-[#E2EAE8] transition-colors group-hover:text-[#B5D6D0]"
    >
      {{ stepNumber }}
    </span>

    <div v-if="isActive" class="mt-6">
      <span class="text-[12px] font-semibold tracking-wide text-[#0F766E]">{{ tier.weight }}</span>
      <h3 class="mt-2.5 text-[24px] font-medium leading-[1.15] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        {{ tier.title }}
      </h3>
      <p class="mt-3 text-[13.5px] leading-[1.6] text-[#5E5A6B]">
        {{ tier.description }}
      </p>
    </div>

    <div v-else class="mt-8">
      <h3 class="text-[15px] font-medium leading-[1.3] text-[#14111C]">
        {{ tier.shortTitle }}
      </h3>
    </div>
  </button>
</template>
