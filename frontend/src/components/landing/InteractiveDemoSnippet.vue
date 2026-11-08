<script setup lang="ts">
import { ref } from "vue";
import { demoSamples, type DemoSample } from "./demoSnippetData";
import InteractiveDemoMatchPanel from "./InteractiveDemoMatchPanel.vue";

const activeTab = ref<"T1" | "T2" | "T3">("T1");
const currentSample = ref<DemoSample>(demoSamples[0]);

function selectSample(id: "T1" | "T2" | "T3") {
  activeTab.value = id;
  const found = demoSamples.find((s) => s.id === id);
  if (found) currentSample.value = found;
}
</script>

<template>
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 select-none" aria-label="Simulasi Diagnostik Naskah">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#ededed] pb-6 mb-8">
      <div class="space-y-2">
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
          <span>Inspeksi Dokumen Real-Time</span>
        </div>
        <h2 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
          Cara Kerja Engine <span class="italic font-normal text-[#17191c]">Mendiagnosis Naskah</span>
        </h2>
        <p class="text-sm text-[#777b86] font-normal max-w-xl">
          Pilih salah satu tingkat pengujian untuk melihat bagaimana sistem menandai kalimat secara transparan bersama bukti pembandingnya.
        </p>
      </div>

      <!-- Segmented Pill Tabs -->
      <div class="inline-flex p-1 bg-[#f2f2f3] rounded-full border border-[#ededed] self-start md:self-auto gap-1">
        <button
          v-for="s in demoSamples"
          :key="s.id"
          type="button"
          :class="[
            'px-4 py-2 text-xs font-medium rounded-full transition-all duration-150 ease-out select-none',
            'focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c]',
            activeTab === s.id
              ? 'bg-[#17191c] text-white shadow-sm'
              : 'text-[#777b86] hover:text-[#17191c] hover:bg-white/50'
          ]"
          @click="selectSample(s.id)"
        >
          <span class="font-semibold">{{ s.tierNumber }}:</span> {{ s.tierName }}
        </button>
      </div>
    </div>

    <!-- Editorial Manuscript Inspection Canvas -->
    <div class="bg-white rounded-[28px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_40px_-15px_rgba(0,0,0,0.08)] overflow-hidden">
      <!-- Canvas Top Metadata Bar -->
      <div class="h-11 bg-[#fafafb] border-b border-[#ededed] px-6 flex items-center justify-between text-xs text-[#777b86]">
        <div class="flex items-center space-x-3">
          <span class="font-medium text-[#17191c]">Naskah Uji vs Repositori Korpus</span>
          <span class="text-[#ededed]">-</span>
          <span class="inline-flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: currentSample.colorHex }"></span>
            <span class="font-medium text-[#17191c]">{{ currentSample.badgeLabel }}</span>
          </span>
        </div>
        <div class="hidden sm:flex items-center space-x-2 font-mono text-[11px]">
          <span>Algoritma: <strong class="text-[#17191c]">{{ currentSample.algorithmName }}</strong></span>
        </div>
      </div>

      <!-- Main Split View: Left Document Passage, Right Side-by-Side Match -->
      <div class="grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-[#ededed]">
        <!-- Left Column: Authentic Manuscript Excerpt (7 Cols) -->
        <div class="lg:col-span-7 p-6 sm:p-8 space-y-5 bg-white">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold text-[#979799] uppercase tracking-wider font-mono">
              Fragmen Naskah Dokumen
            </span>
            <span class="text-[11px] text-[#777b86]">Bab II - Tinjauan Pustaka</span>
          </div>

          <!-- Document Paragraph with Editorial Highlight -->
          <div class="p-6 rounded-[20px] bg-[#fafafb] border border-[#ededed] leading-relaxed text-sm sm:text-base text-[#17191c]">
            <span class="text-[#777b86]">{{ currentSample.originalText }}</span>
            <mark
              :class="[
                'px-1.5 py-0.5 rounded-md font-medium border-b-2 transition-colors duration-150',
                currentSample.highlightBg,
                currentSample.highlightBorder
              ]"
            >
              "{{ currentSample.highlightedSpan }}"
            </mark>
            <span class="text-[#777b86]">{{ currentSample.postText }}</span>
          </div>

          <!-- Diagnostic Note Callout -->
          <div class="p-4 rounded-[16px] border border-[#ededed] bg-white flex items-start space-x-3">
            <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-white text-xs font-bold" :style="{ backgroundColor: currentSample.colorHex }">
              !
            </div>
            <div class="space-y-0.5 text-xs">
              <div class="font-semibold text-[#17191c]">Catatan Hasil Diagnosis:</div>
              <p class="text-[#777b86] leading-relaxed font-normal">
                {{ currentSample.diagnosticNote }}
              </p>
            </div>
          </div>
        </div>

        <!-- Right Column: Extracted Component -->
        <InteractiveDemoMatchPanel :sample="currentSample" />
      </div>
    </div>
  </section>
</template>
