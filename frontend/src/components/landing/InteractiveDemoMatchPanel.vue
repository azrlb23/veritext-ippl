<script setup lang="ts">
import type { DemoSample } from "./demoSnippetData";

defineProps<{
  sample: DemoSample;
}>();
</script>

<template>
  <div class="lg:col-span-5 p-6 sm:p-8 space-y-6 bg-[#fafafb] flex flex-col justify-between">
    <div class="space-y-5">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-bold text-[#979799] uppercase tracking-wider font-mono">
          Rujukan Pembanding Korpus
        </span>
        <span class="text-xs font-bold tabular-nums px-2.5 py-0.5 rounded-full bg-white border border-[#ededed]" :style="{ color: sample.colorHex }">
          {{ sample.similarityScore }}% Kecocokan
        </span>
      </div>

      <!-- Matched Snippet Box -->
      <div class="p-5 rounded-[20px] bg-white border border-[#ededed] space-y-2 shadow-sm">
        <div class="text-[11px] font-semibold text-[#17191c] truncate">
          {{ sample.matchedSource }}
        </div>
        <div class="text-[10px] text-[#777b86] -mt-1">
          {{ sample.matchedAuthor }}
        </div>
        <p class="text-xs text-[#515151] italic leading-relaxed pt-2 border-t border-[#ededed]">
          "{{ sample.matchedSnippet }}"
        </p>
      </div>

      <!-- Technical Parameter Checklist -->
      <div class="space-y-2 text-xs">
        <div class="flex items-center justify-between py-1.5 border-b border-[#ededed]">
          <span class="text-[#777b86]">Metrik Nilai</span>
          <span class="font-mono font-medium text-[#17191c] tabular-nums">{{ sample.engineMetric }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5 border-b border-[#ededed]">
          <span class="text-[#777b86]">Algoritma Inti</span>
          <span class="font-medium text-[#17191c]">{{ sample.algorithmName }}</span>
        </div>
        <div class="flex items-center justify-between py-1.5">
          <span class="text-[#777b86]">Bobot Komposit</span>
          <span class="font-semibold text-[#17191c] tabular-nums">
            {{ sample.id === 'T1' ? '50%' : sample.id === 'T2' ? '35%' : '15%' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Bottom Action Link -->
    <div class="pt-4 border-t border-[#ededed]">
      <router-link
        to="/dashboard"
        class="w-full inline-flex items-center justify-center px-4 py-2.5 rounded-full bg-[#17191c] hover:bg-[#2b2e34] text-white text-xs font-medium transition-colors"
      >
        <span>Coba Uji Naskah Lengkap di Workspace</span>
        <span class="ml-1.5">&rarr;</span>
      </router-link>
    </div>
  </div>
</template>
