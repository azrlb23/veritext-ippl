<script setup lang="ts">
import { computed } from "vue";
import type { TrendPoint } from "../../types/admin";

const props = defineProps<{ trends: TrendPoint[]; loading?: boolean }>();

const W = 420;
const H = 140;
const PAD_X = 10;
const PAD_Y = 12;

const safeTrends = computed(() => props.trends || []);
const totalAudits = computed(() => safeTrends.value.reduce((acc, p) => acc + (p.audits || 0), 0));
const totalRevenue = computed(() => safeTrends.value.reduce((acc, p) => acc + (p.revenue || 0), 0));
const maxAudits = computed(() => Math.max(1, ...safeTrends.value.map((p) => p.audits || 0)));
const maxRevenue = computed(() => Math.max(1, ...safeTrends.value.map((p) => p.revenue || 0)));

const shortDate = (iso: string) => {
  if (!iso) return "";
  const d = new Date(`${iso.slice(0, 10)}T00:00:00`);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString("id-ID", { day: "numeric", month: "short" });
};

const dateLabels = computed(() => {
  const list = safeTrends.value;
  if (list.length === 0) return { start: "-", mid: "-", end: "-" };
  const midIdx = Math.floor((list.length - 1) / 2);
  return {
    start: shortDate(list[0].date),
    mid: shortDate(list[midIdx].date),
    end: shortDate(list[list.length - 1].date),
  };
});

const auditBars = computed(() => {
  const list = safeTrends.value;
  if (!list.length) return [];
  const plotW = W - PAD_X * 2;
  const plotH = H - PAD_Y * 2;
  const step = plotW / list.length;
  const barW = Math.max(6, Math.min(18, step * 0.62));
  return list.map((p, i) => {
    const val = p.audits || 0;
    const h = val > 0 ? Math.max(4, (val / maxAudits.value) * plotH) : 2;
    const x = PAD_X + i * step + (step - barW) / 2;
    const y = H - PAD_Y - h;
    return { x, y, w: barW, h, label: `${shortDate(p.date)}: ${val.toLocaleString("id-ID")} pemeriksaan` };
  });
});

const revPoints = computed(() => {
  const list = safeTrends.value;
  if (!list.length) return [];
  const plotW = W - PAD_X * 2;
  const plotH = H - PAD_Y * 2;
  const denom = Math.max(1, list.length - 1);
  return list.map((p, i) => {
    const val = p.revenue || 0;
    const x = list.length === 1 ? W / 2 : PAD_X + (i / denom) * plotW;
    const y = H - PAD_Y - (val / maxRevenue.value) * plotH;
    return { x, y, label: `${shortDate(p.date)}: Rp ${val.toLocaleString("id-ID")}` };
  });
});

const revLine = computed(() => revPoints.value.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" "));
const revArea = computed(() => {
  const pts = revPoints.value;
  if (!pts.length) return "";
  const base = H - PAD_Y;
  return `M ${pts[0].x.toFixed(1)},${base} L ${pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" L ")} L ${pts[pts.length - 1].x.toFixed(1)},${base} Z`;
});

const rupiah = (n: number) => `Rp ${(n || 0).toLocaleString("id-ID")}`;
</script>

<template>
  <section class="rounded-[28px] border border-[#E8ECEB] bg-white p-6 sm:p-8" aria-labelledby="trend-title" :aria-busy="loading">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 id="trend-title" class="text-[20px] font-semibold tracking-[-0.03em] text-[#14111C]">Tren 14 hari terakhir</h2>
      <p class="text-[13px] text-[#5E5A6B]">Pemeriksaan naskah &amp; pendapatan harian</p>
    </div>

    <p v-if="!loading && safeTrends.length === 0" class="py-10 text-center text-[14px] text-[#5E5A6B]">Data tren belum tersedia.</p>

    <div v-else class="mt-6 grid grid-cols-1 gap-8 divide-[#E8ECEB] lg:grid-cols-2 lg:gap-0 lg:divide-x">
      <div class="lg:pr-8">
        <div class="flex items-baseline justify-between gap-4">
          <p class="text-[14px] font-medium text-[#4B4757]">Pemeriksaan harian</p>
          <p class="text-[20px] font-semibold tracking-[-0.03em] tabular-nums text-[#0F766E]">
            {{ loading ? "-" : totalAudits.toLocaleString("id-ID") }}
            <span class="ml-1 text-[12px] font-normal text-[#5E5A6B]">total</span>
          </p>
        </div>
        <svg :viewBox="`0 0 ${W} ${H}`" class="mt-3 h-36 w-full overflow-visible" role="img" :aria-label="`Grafik batang pemeriksaan 14 hari, total ${totalAudits.toLocaleString('id-ID')} pemeriksaan`">
          <line :x1="PAD_X" :y1="H - PAD_Y" :x2="W - PAD_X" :y2="H - PAD_Y" stroke="#E8ECEB" stroke-width="1" />
          <line :x1="PAD_X" :y1="PAD_Y + (H - PAD_Y * 2) / 2" :x2="W - PAD_X" :y2="PAD_Y + (H - PAD_Y * 2) / 2" stroke="#E8ECEB" stroke-dasharray="3 3" stroke-width="1" />
          <rect v-for="(b, idx) in auditBars" :key="idx" :x="b.x" :y="b.y" :width="b.w" :height="b.h" rx="3" fill="#0F766E">
            <title>{{ b.label }}</title>
          </rect>
        </svg>
        <div class="mt-2 flex items-center justify-between text-[12px] tabular-nums text-[#5E5A6B]">
          <span>{{ dateLabels.start }}</span>
          <span>{{ dateLabels.mid }}</span>
          <span>{{ dateLabels.end }}</span>
        </div>
      </div>

      <div class="lg:pl-8">
        <div class="flex items-baseline justify-between gap-4">
          <p class="text-[14px] font-medium text-[#4B4757]">Pendapatan harian</p>
          <p class="text-[20px] font-semibold tracking-[-0.03em] tabular-nums text-[#D97706]">
            {{ loading ? "-" : rupiah(totalRevenue) }}
          </p>
        </div>
        <svg :viewBox="`0 0 ${W} ${H}`" class="mt-3 h-36 w-full overflow-visible" role="img" :aria-label="`Grafik garis pendapatan 14 hari, total ${rupiah(totalRevenue)}`">
          <line :x1="PAD_X" :y1="H - PAD_Y" :x2="W - PAD_X" :y2="H - PAD_Y" stroke="#E8ECEB" stroke-width="1" />
          <line :x1="PAD_X" :y1="PAD_Y + (H - PAD_Y * 2) / 2" :x2="W - PAD_X" :y2="PAD_Y + (H - PAD_Y * 2) / 2" stroke="#E8ECEB" stroke-dasharray="3 3" stroke-width="1" />
          <path v-if="revArea" :d="revArea" fill="#D97706" fill-opacity="0.12" />
          <polyline v-if="revLine" :points="revLine" fill="none" stroke="#D97706" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round" />
          <circle v-for="(p, idx) in revPoints" :key="idx" :cx="p.x" :cy="p.y" r="3" fill="#D97706">
            <title>{{ p.label }}</title>
          </circle>
        </svg>
        <div class="mt-2 flex items-center justify-between text-[12px] tabular-nums text-[#5E5A6B]">
          <span>{{ dateLabels.start }}</span>
          <span>{{ dateLabels.mid }}</span>
          <span>{{ dateLabels.end }}</span>
        </div>
      </div>
    </div>
  </section>
</template>
