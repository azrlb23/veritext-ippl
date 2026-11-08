<script setup lang="ts">
import { computed, reactive } from "vue";
import type { HeatmapAnnotation } from "../../types";

const props = defineProps<{ text?: string | null; annotations: HeatmapAnnotation[]; selected?: HeatmapAnnotation | null }>();
const emit = defineEmits<{ (e: "select", a: HeatmapAnnotation): void }>();

type Kind = "RED" | "ORANGE" | "YELLOW" | "RESOLVED_GREEN";
const layers = reactive<Record<Kind, boolean>>({ RED: true, ORANGE: true, YELLOW: true, RESOLVED_GREEN: true });
const KINDS: { key: Kind; label: string; bg: string }[] = [
  { key: "RED", label: "Kata sama", bg: "bg-[#FEE2E2]" },
  { key: "ORANGE", label: "Makna sama", bg: "bg-[#FFEDD5]" },
  { key: "YELLOW", label: "Pola AI", bg: "bg-[#FEF3C7]" },
  { key: "RESOLVED_GREEN", label: "Sudah diperbaiki", bg: "bg-[#DCFCE7]" },
];

function kindOf(a: HeatmapAnnotation): Kind {
  if (a.color === "RESOLVED_GREEN" || (a as any).match_type === "RESOLVED_GREEN") return "RESOLVED_GREEN";
  if (a.color === "RED" || a.tier === "T1") return "RED";
  if (a.color === "ORANGE" || a.tier === "T2") return "ORANGE";
  return "YELLOW";
}
const bgOf = (a: HeatmapAnnotation) => KINDS.find((k) => k.key === kindOf(a))!.bg;
const isSelected = (a: HeatmapAnnotation) => !!props.selected && props.selected.start === a.start && props.selected.end === a.end;

const slices = computed(() => {
  const raw = props.text || "";
  const out: { text: string; anno?: HeatmapAnnotation }[] = [];
  let pos = 0;
  for (const a of [...props.annotations].sort((x, y) => x.start - y.start)) {
    const s = Math.max(pos, Math.min(a.start, raw.length));
    const e = Math.max(s, Math.min(a.end, raw.length));
    if (s > pos) out.push({ text: raw.slice(pos, s) });
    if (e > s) out.push({ text: raw.slice(s, e), anno: a });
    pos = Math.max(pos, e);
  }
  if (pos < raw.length) out.push({ text: raw.slice(pos) });
  return out;
});
</script>

<template>
  <section class="rounded-[32px] bg-white p-5 shadow-float sm:p-8" aria-label="Naskah dengan sorotan">
    <div class="flex flex-wrap gap-2" role="group" aria-label="Saring sorotan">
      <button
        v-for="k in KINDS"
        :key="k.key"
        type="button"
        :aria-pressed="layers[k.key]"
        class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        :class="[k.bg, layers[k.key] ? '' : 'opacity-40']"
        @click="layers[k.key] = !layers[k.key]"
      >{{ k.label }}</button>
    </div>
    <div class="mt-6 max-h-[640px] overflow-y-auto whitespace-pre-wrap text-[16px] leading-[2] text-[#14111C]">
      <template v-if="text">
        <template v-for="(s, i) in slices" :key="i">
          <span
            v-if="s.anno"
            role="button"
            tabindex="0"
            class="cursor-pointer rounded-md px-0.5 transition-colors box-decoration-clone focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            :class="[layers[kindOf(s.anno)] ? bgOf(s.anno) : '', isSelected(s.anno) ? 'ring-2 ring-[#14111C]' : '']"
            @click="emit('select', s.anno)"
            @keydown.enter.prevent="emit('select', s.anno)"
          >{{ s.text }}</span>
          <span v-else>{{ s.text }}</span>
        </template>
      </template>
      <p v-else class="py-16 text-center text-[15px] text-[#5E5A6B]">Teks naskah tidak tersedia untuk ditampilkan.</p>
    </div>
  </section>
</template>
