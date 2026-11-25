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
  <div>
    <div class="mb-3 text-[13px] font-medium text-[#5E5A6B]">Kedalaman pemeriksaan</div>
    <div role="radiogroup" aria-label="Kedalaman pemeriksaan" class="space-y-2">
      <button
        v-for="o in options"
        :key="o.key"
        type="button"
        role="radio"
        :aria-checked="modelValue === o.key"
        class="flex w-full cursor-pointer items-start justify-between gap-4 rounded-2xl px-4 py-4 text-left transition-all duration-200 focus:outline-none"
        :class="modelValue === o.key
          ? 'bg-white/75 shadow-[0_6px_20px_-6px_rgba(15,118,110,0.14)] backdrop-blur-sm'
          : 'bg-transparent hover:bg-white/40'"
        @click="$emit('update:modelValue', o.key)"
      >
        <div class="flex items-start gap-3">
          <span
            class="mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border transition-colors"
            :class="modelValue === o.key ? 'border-[#0F766E]/70 bg-[#0F766E]/10' : 'border-[#CBD5E1]'"
            aria-hidden="true"
          >
            <span v-if="modelValue === o.key" class="h-2 w-2 rounded-full bg-[#0F766E]" />
          </span>
          <div>
            <div class="text-[15.5px] font-semibold tracking-[-0.015em] text-[#14111C]">{{ o.title }}</div>
            <p class="mt-0.5 text-[13.5px] leading-[1.5] text-[#4B4757]">{{ o.desc }}</p>
          </div>
        </div>
        <span
          class="mt-0.5 shrink-0 text-[12.5px] font-medium"
          :class="modelValue === o.key ? 'text-[#0F766E]' : 'text-[#5E5A6B]'"
        >
          {{ o.note }}
        </span>
      </button>
    </div>
  </div>
</template>
