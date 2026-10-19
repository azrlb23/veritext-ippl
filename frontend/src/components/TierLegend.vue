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
  <div class="bg-white border border-[#ededed] rounded-[24px] p-6 sm:p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h4 class="text-xs font-semibold uppercase tracking-wider text-[#17191c]">
          Legenda Tier Deteksi Plagiarisme (SDD 3.6.2)
        </h4>
        <p class="text-[11px] text-[#777b86] mt-0.5">Klasifikasi tingkat keparahan dan pembobotan skor</p>
      </div>
      <span v-if="showControls" class="text-[11px] text-[#17191c] italic font-medium px-3 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed]">Klik untuk menyaring</span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Tier 1: Lexical Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] hover:bg-white hover:border-[#17191c] transition-all duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T1 }
        ]"
        @click="showControls && handleToggle('T1')"
        @keydown.enter="showControls && handleToggle('T1')"
        @keydown.space.prevent="showControls && handleToggle('T1')"
      >
        <div class="w-4 h-4 rounded-[4px] bg-[#EF4444] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-[#17191c]">Tier 1: Leksikal</span>
            <span class="text-[10px] tabular-nums px-2.5 py-0.5 bg-[#fef2f2] text-[#b91c1c] border border-[#fee2e2] rounded-full font-medium">#EF4444</span>
          </div>
          <p class="text-[11px] text-[#777b86] leading-relaxed">
            Penjiplakan <em class="italic font-medium">verbatim</em> / salin-tempel langsung (Winnowing k=5, w=4).
          </p>
        </div>
      </div>

      <!-- Tier 2: Semantic Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] hover:bg-white hover:border-[#17191c] transition-all duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T2 }
        ]"
        @click="showControls && handleToggle('T2')"
        @keydown.enter="showControls && handleToggle('T2')"
        @keydown.space.prevent="showControls && handleToggle('T2')"
      >
        <div class="w-4 h-4 rounded-[4px] bg-[#F97316] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-[#17191c]">Tier 2: Semantik</span>
            <span class="text-[10px] tabular-nums px-2.5 py-0.5 bg-[#fff7ed] text-[#c2410c] border border-[#ffedd5] rounded-full font-medium">#F97316</span>
          </div>
          <p class="text-[11px] text-[#777b86] leading-relaxed">
            Parafrasa cerdas (<span class="italic font-medium">Sentence Transformers MiniLM-L12 + pgvector</span>).
          </p>
        </div>
      </div>

      <!-- Tier 3: AI / Stylometric Card -->
      <div
        :role="showControls ? 'button' : undefined"
        :tabindex="showControls ? 0 : undefined"
        class="flex items-start space-x-3.5 p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] hover:bg-white hover:border-[#17191c] transition-all duration-150 ease-out select-none"
        :class="[
          showControls ? 'cursor-pointer active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]' : '',
          { 'opacity-40 grayscale-[30%]': !activeTiers.T3 }
        ]"
        @click="showControls && handleToggle('T3')"
        @keydown.enter="showControls && handleToggle('T3')"
        @keydown.space.prevent="showControls && handleToggle('T3')"
      >
        <div class="w-4 h-4 rounded-[4px] bg-[#EAB308] flex-shrink-0 mt-0.5"></div>
        <div class="space-y-1 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-[#17191c]">Tier 3: Anomali AI</span>
            <span class="text-[10px] tabular-nums px-2.5 py-0.5 bg-[#fefce8] text-[#854d0e] border border-[#fef08a] rounded-full font-medium">#EAB308</span>
          </div>
          <p class="text-[11px] text-[#777b86] leading-relaxed">
            Pola sintaksis LLM (<span class="italic font-medium">Analisis Burstiness &amp; Type-Token Ratio</span>).
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
