<script setup lang="ts">
import { ref } from "vue";

const selectedRange = ref("8 bulan");
const activeMonthIndex = ref(6);

const monthlyData = [
  { month: "Apr", count: 1, score: "18.2%" }, { month: "Mei", count: 0, score: "-" },
  { month: "Jun", count: 2, score: "14.5%" }, { month: "Jul", count: 1, score: "19.0%" },
  { month: "Agu", count: 2, score: "16.8%" }, { month: "Sep", count: 1, score: "22.1%" },
  { month: "Okt", count: 4, score: "21.4%" }, { month: "Nov", count: 3, score: "17.9%" },
];
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 font-sans select-none items-stretch">
    <div class="lg:col-span-8 bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-slate-900">Aktivitas Pengujian Naskah</h2>
          <p class="text-xs text-slate-500">Tren volume pemeriksaan berkas bulanan</p>
        </div>
        <span class="px-3 py-1 rounded-full bg-slate-100 text-xs font-semibold text-slate-700 border border-slate-200">{{ selectedRange }}</span>
      </div>

      <div class="relative pt-6 pb-2">
        <div class="space-y-5 border-b border-slate-100 pb-2">
          <div v-for="level in [5, 4, 3, 2, 1, 0]" :key="level" class="flex items-center gap-3">
            <span class="w-4 text-right text-xs text-slate-400 font-mono">{{ level }}</span>
            <div class="flex-1 border-b border-dashed border-slate-200"></div>
          </div>
        </div>

        <div class="absolute inset-x-8 bottom-6 top-6 flex items-end justify-between px-2 sm:px-6">
          <div v-for="(item, idx) in monthlyData" :key="item.month" class="relative flex flex-col items-center group cursor-pointer" @mouseenter="activeMonthIndex = idx">
            <div class="w-9 sm:w-12 h-44 bg-slate-100 rounded-xl relative flex items-end justify-center p-1">
              <div v-if="item.count > 0" class="w-full rounded-lg transition-all"
                :class="idx === activeMonthIndex ? 'bg-blue-600 shadow-sm' : 'bg-slate-300 group-hover:bg-slate-400'"
                :style="{ height: `${(item.count / 5) * 100}%` }">
                <div v-if="idx === activeMonthIndex" class="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-white border-2 border-blue-600"></div>
              </div>
              <div v-if="idx === activeMonthIndex" class="absolute -top-16 left-1/2 -translate-x-1/2 z-20 bg-white border border-slate-200 shadow-lg rounded-xl p-2.5 w-36 pointer-events-none text-left">
                <div class="text-[11px] font-bold text-slate-900">{{ item.month }} 2026</div>
                <div class="text-[10px] text-slate-500 flex justify-between mt-1"><span>Diuji:</span><strong class="text-slate-900">{{ item.count }}</strong></div>
                <div class="text-[10px] text-slate-500 flex justify-between"><span>Rerata:</span><strong class="text-slate-900">{{ item.score }}</strong></div>
              </div>
            </div>
            <span class="text-xs mt-2 font-medium" :class="idx === activeMonthIndex ? 'text-slate-900 font-bold' : 'text-slate-500'">{{ item.month }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="lg:col-span-4 bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Tingkat Keaslian</h2>
        <p class="text-xs text-slate-500">Proporsi naskah memenuhi standar</p>
      </div>

      <div class="relative w-36 h-36 mx-auto my-1 flex items-center justify-center">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="38" stroke="#E2E8F0" stroke-width="10" fill="none" stroke-dasharray="4 2" />
          <circle cx="50" cy="50" r="38" stroke="#1560BD" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="179 239" />
        </svg>
        <div class="absolute text-center flex flex-col items-center">
          <span class="text-3xl font-extrabold text-slate-900 tracking-tight">75%</span>
          <span class="text-[11px] text-emerald-600 font-bold">Naskah Aman</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 pt-1">
        <div class="bg-slate-50 rounded-2xl p-3.5 space-y-0.5 border border-slate-200">
          <div class="text-[11px] font-semibold text-slate-500">Aman (&lt;20%)</div>
          <div class="text-xl font-bold text-emerald-600">9</div>
          <div class="text-[10px] text-slate-400">75% dari 12 audit</div>
        </div>
        <div class="bg-slate-50 rounded-2xl p-3.5 space-y-0.5 border border-slate-200">
          <div class="text-[11px] font-semibold text-slate-500">Perlu Ditinjau</div>
          <div class="text-xl font-bold text-orange-600">3</div>
          <div class="text-[10px] text-slate-400">25% dari 12 audit</div>
        </div>
      </div>
    </div>
  </div>
</template>
