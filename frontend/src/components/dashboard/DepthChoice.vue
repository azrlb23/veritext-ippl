<script setup lang="ts">
type Depth = "FULL" | "TIER1_ONLY";

defineProps<{ modelValue: Depth }>();
defineEmits<{ (e: "update:modelValue", value: Depth): void }>();

const options: { key: Depth; title: string; desc: string; note: string }[] = [
  { key: "FULL", title: "Audit penuh", desc: "Kecocokan kata, makna, pola tulisan AI, dan pencarian web", note: "Paling lengkap" },
  { key: "TIER1_ONLY", title: "Pindai cepat", desc: "Kecocokan kata dan pola dasar, tanpa pencarian web", note: "Lebih singkat" },
];
</script>

<template>
  <div role="radiogroup" aria-label="Kedalaman pemeriksaan" class="grid gap-3 sm:grid-cols-2">
    <button
      v-for="o in options"
      :key="o.key"
      type="button"
      role="radio"
      :aria-checked="modelValue === o.key"
      class="flex min-h-[132px] cursor-pointer flex-col justify-between rounded-[24px] p-5 text-left transition-all duration-300 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
      :class="modelValue === o.key
        ? 'bg-gradient-to-br from-[#7A2FD6] to-[#9B4FE6] text-white shadow-[0_24px_44px_-18px_rgba(122,47,214,0.55)]'
        : 'bg-white text-[#14111C] shadow-lift hover:-translate-y-0.5'"
      @click="$emit('update:modelValue', o.key)"
    >
      <div>
        <div class="text-[17px] font-semibold tracking-[-0.02em]">{{ o.title }}</div>
        <p class="mt-1 text-[13.5px] leading-[1.55]" :class="modelValue === o.key ? 'text-white/85' : 'text-[#4B4757]'">{{ o.desc }}</p>
      </div>
      <div class="mt-4 text-[13px] font-medium" :class="modelValue === o.key ? 'text-white/80' : 'text-[#5E5A6B]'">{{ o.note }}</div>
    </button>
  </div>
</template>
