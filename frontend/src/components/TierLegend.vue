<script setup lang="ts">
import { ref } from "vue";

withDefaults(
  defineProps<{
    showControls?: boolean;
  }>(),
  {
    showControls: false,
  }
);

const emit = defineEmits<{
  (e: "toggleTier", tier: "T1" | "T2" | "T3", visible: boolean): void;
}>();

const activeTiers = ref({
  T1: true,
  T2: true,
  T3: true,
});

function handleToggle(tier: "T1" | "T2" | "T3") {
  activeTiers.value[tier] = !activeTiers.value[tier];
  emit("toggleTier", tier, activeTiers.value[tier]);
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] p-5 sm:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h4 class="text-xs font-extrabold uppercase tracking-wider text-[#262626]">
          Legenda Tier Deteksi Plagiarisme (SDD 3.6.2)
        </h4>
        <p class="text-[11px] text-[#737373] mt-0.5">Klasifikasi tingkat keparahan dan pembobotan skor</p>
      </div>
      <span v-if="showControls" class="text-[11px] text-[#262626] italic font-bold px-2.5 py-1 rounded-full bg-[#ededed] border border-[#ededed]">Klik untuk menyaring</span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Tier 1: Lexical Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[8px] border border-[#ededed] bg-white hover:bg-[#fafafa] transition-colors duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T1 }
        ]"
        @click="showControls && handleToggle('T1')"
        @keydown.enter="showControls && handleToggle('T1')"
        @keydown.space.prevent="showControls && handleToggle('T1')"
      >
        <div class="w-4 h-4 rounded-[3px] bg-[#EF4444] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-[#262626]">Tier 1: Leksikal</span>
            <span class="text-[10px] tabular-nums px-2 py-0.5 bg-[#fef2f2] text-[#b91c1c] border border-[#fee2e2] rounded-full font-bold">#EF4444</span>
          </div>
          <p class="text-[11px] text-[#686868] leading-relaxed">
            Penjiplakan <em class="italic font-bold">verbatim</em> / salin-tempel langsung (Winnowing k=5, w=4).
          </p>
        </div>
      </div>

      <!-- Tier 2: Semantic Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[8px] border border-[#ededed] bg-white hover:bg-[#fafafa] transition-colors duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T2 }
        ]"
        @click="showControls && handleToggle('T2')"
        @keydown.enter="showControls && handleToggle('T2')"
        @keydown.space.prevent="showControls && handleToggle('T2')"
      >
        <div class="w-4 h-4 rounded-[3px] bg-[#F97316] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-[#262626]">Tier 2: Semantik</span>
            <span class="text-[10px] tabular-nums px-2 py-0.5 bg-[#fff7ed] text-[#c2410c] border border-[#ffedd5] rounded-full font-bold">#F97316</span>
          </div>
          <p class="text-[11px] text-[#686868] leading-relaxed">
            Parafrasa cerdas (<span class="italic font-bold">Sentence Transformers MiniLM-L12 + pgvector</span>).
          </p>
        </div>
      </div>

      <!-- Tier 3: AI / Stylometric Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[8px] border border-[#ededed] bg-white hover:bg-[#fafafa] transition-colors duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T3 }
        ]"
        @click="showControls && handleToggle('T3')"
        @keydown.enter="showControls && handleToggle('T3')"
        @keydown.space.prevent="showControls && handleToggle('T3')"
      >
        <div class="w-4 h-4 rounded-[3px] bg-[#EAB308] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-[#262626]">Tier 3: Anomali AI</span>
            <span class="text-[10px] tabular-nums px-2 py-0.5 bg-[#fefce8] text-[#854d0e] border border-[#fef08a] rounded-full font-bold">#EAB308</span>
          </div>
          <p class="text-[11px] text-[#686868] leading-relaxed">
            Pola sintaksis LLM (<span class="italic font-bold">Analisis Burstiness &amp; Type-Token Ratio</span>).
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
