<script setup lang="ts">
import { VtIcon, type VtIconName } from "../common";

type BadgeTarget = "sentence" | "report" | "paraphrase" | "verified";

defineProps<{ activeTarget: string }>();
const emit = defineEmits<{ (e: "select", target: BadgeTarget): void }>();

const badges: Array<{
  icon: VtIconName;
  label: string;
  arc: string;
  target: BadgeTarget;
}> = [
  { icon: "lexical", label: "Kata", arc: "-rotate-6 translate-y-2", target: "sentence" },
  { icon: "semantic", label: "Makna", arc: "-rotate-3 translate-y-0.5", target: "sentence" },
  { icon: "stylometric", label: "Gaya AI", arc: "rotate-0 -translate-y-1", target: "report" },
  { icon: "rewrite", label: "Parafrase", arc: "rotate-3 translate-y-0.5", target: "paraphrase" },
  { icon: "verified", label: "Sertifikat", arc: "rotate-6 translate-y-2", target: "verified" },
];
</script>

<template>
  <div class="flex items-center justify-center gap-2.5 sm:gap-3.5" role="group" aria-label="Navigasi fitur cepat">
    <div v-for="item in badges" :key="item.icon" :class="item.arc">
      <button
        type="button"
        :title="item.label"
        :aria-label="item.label"
        class="flex h-11 w-11 cursor-pointer items-center justify-center rounded-2xl border bg-white shadow-lift transition-[transform,box-shadow,border-color,color] duration-200 hover:-translate-y-1 hover:border-[#0F766E]/40 hover:text-[#0F766E] hover:shadow-float sm:h-12 sm:w-12"
        :class="
          activeTarget === item.target
            ? 'border-[#0F766E]/40 text-[#0F766E] -translate-y-1 shadow-float'
            : 'border-[#E4EEEC] text-[#5E5A6B]'
        "
        @click="emit('select', item.target)"
      >
        <VtIcon :name="item.icon" tone="current" class="h-5 w-5" />
      </button>
    </div>
  </div>
</template>
