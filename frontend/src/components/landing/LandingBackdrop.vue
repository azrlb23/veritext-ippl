<script setup lang="ts">
// Latar satu halaman penuh: sapuan warna di bawah, ubin kaca di atasnya.
// Semuanya memudar tanpa tepi sehingga seksi di atasnya menyatu dengan halaman.
import GlassTileField from "./GlassTileField.vue";

const props = defineProps<{ variant?: "home" | "page" }>();

const LEFT = "radial-gradient(ellipse 100% 60% at 0% 50%, #000 0%, #000 35%, transparent 100%)";
const RIGHT = "radial-gradient(ellipse 100% 60% at 100% 50%, #000 0%, #000 35%, transparent 100%)";
const BOTTOM = "radial-gradient(ellipse 65% 100% at 50% 100%, #000 0%, #000 30%, transparent 100%)";

const homeBlobs = [
  "-right-32 top-[1%] h-[460px] w-[560px] bg-[#8FA8F5] opacity-60",
  "-left-40 top-[13%] h-[640px] w-[900px] bg-[#8A3FE0] opacity-55",
  "right-[8%] top-[17%] h-[360px] w-[540px] bg-[#D26BE6] opacity-40",
  "-right-40 top-[34%] h-[520px] w-[620px] bg-[#8FA8F5] opacity-40",
  "-left-56 top-[50%] h-[640px] w-[860px] bg-[#8A3FE0] opacity-25",
  "left-[10%] top-[72%] h-[520px] w-[1100px] bg-[#C9A0F0] opacity-45",
  "-right-32 top-[86%] h-[420px] w-[560px] bg-[#8FA8F5] opacity-35",
];
const pageBlobs = [
  "-right-32 top-[1%] h-[420px] w-[520px] bg-[#8FA8F5] opacity-50",
  "-left-48 top-[16%] h-[480px] w-[680px] bg-[#8A3FE0] opacity-30",
  "right-[8%] top-[34%] h-[320px] w-[480px] bg-[#D26BE6] opacity-20",
  "left-[12%] top-[72%] h-[420px] w-[900px] bg-[#C9A0F0] opacity-40",
];

const homeFields = [
  { pos: "left-0 top-[27%]", cols: 4, rows: 6, mask: LEFT, seed: 3 },
  { pos: "right-0 top-[40%]", cols: 4, rows: 6, mask: RIGHT, seed: 5 },
  { pos: "left-0 top-[56%]", cols: 4, rows: 6, mask: LEFT, seed: 9 },
  { pos: "right-0 top-[73%]", cols: 4, rows: 5, mask: RIGHT, seed: 13 },
];
const pageFields = [
  { pos: "right-0 top-[1%]", cols: 2, rows: 6, mask: RIGHT, seed: 4 },
  { pos: "left-0 top-[24%]", cols: 2, rows: 6, mask: LEFT, seed: 8 },
  { pos: "right-0 top-[48%]", cols: 2, rows: 5, mask: RIGHT, seed: 12 },
];

const isHome = () => props.variant !== "page";
</script>

<template>
  <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
    <div
      v-for="(b, i) in isHome() ? homeBlobs : pageBlobs"
      :key="'b' + i"
      class="absolute rounded-full blur-[140px]"
      :class="b"
    ></div>

    <GlassTileField
      v-for="(f, i) in isHome() ? homeFields : pageFields"
      :key="'f' + i"
      class="absolute hidden md:grid"
      :class="f.pos"
      :cols="f.cols"
      :rows="f.rows"
      :seed="f.seed"
      :mask="f.mask"
    />

    <GlassTileField class="absolute bottom-0 left-1/2 -translate-x-1/2" :cols="20" :rows="3" :seed="21" :mask="BOTTOM" />
  </div>
</template>
