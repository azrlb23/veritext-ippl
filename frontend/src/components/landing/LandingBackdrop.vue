<script setup lang="ts">
// Latar satu halaman penuh: sapuan warna lembut, tekstur titik/grain, medan ubin kaca, dan kapsul kaca tanpa tepi terpotong.
import { computed } from "vue";
import GlassTileField from "./GlassTileField.vue";
import LandingFloatingIcons from "./LandingFloatingIcons.vue";

const props = defineProps<{ variant?: "home" | "page" | "auth" }>();

const softMask =
  "radial-gradient(ellipse 64% 64% at 50% 50%, #000 0%, #000 22%, transparent 70%)";

function blobStyle(colorRgb: string, opacity: number) {
  const mid = (opacity * 0.42).toFixed(2);
  return {
    background: `radial-gradient(closest-side, rgba(${colorRgb}, ${opacity}) 0%, rgba(${colorRgb}, ${mid}) 45%, rgba(${colorRgb}, 0) 100%)`,
  };
}

const homeBlobs = [
  { pos: "right-[-258px] top-[calc(1%_-_130px)] h-[720px] w-[820px]", rgb: "125, 211, 252", opacity: 0.52 },
  { pos: "left-[-290px] top-[calc(13%_-_130px)] h-[900px] w-[1160px]", rgb: "253, 186, 116", opacity: 0.52 },
  { pos: "right-[calc(8%_-_130px)] top-[calc(17%_-_130px)] h-[620px] w-[800px]", rgb: "20, 184, 166", opacity: 0.42 },
  { pos: "right-[-290px] top-[calc(34%_-_130px)] h-[780px] w-[880px]", rgb: "251, 146, 60", opacity: 0.28 },
  { pos: "left-[-354px] top-[calc(50%_-_130px)] h-[900px] w-[1120px]", rgb: "15, 118, 110", opacity: 0.28 },
  { pos: "left-[calc(10%_-_130px)] top-[calc(72%_-_130px)] h-[780px] w-[1360px]", rgb: "94, 234, 212", opacity: 0.38 },
  { pos: "right-[-258px] top-[calc(86%_-_130px)] h-[680px] w-[820px]", rgb: "253, 186, 116", opacity: 0.36 },
];

const pageBlobs = [
  { pos: "right-[-258px] top-[calc(1%_-_130px)] h-[680px] w-[780px]", rgb: "125, 211, 252", opacity: 0.42 },
  { pos: "left-[-322px] top-[calc(16%_-_130px)] h-[740px] w-[940px]", rgb: "253, 186, 116", opacity: 0.34 },
  { pos: "right-[calc(8%_-_130px)] top-[calc(34%_-_130px)] h-[580px] w-[740px]", rgb: "15, 118, 110", opacity: 0.24 },
  { pos: "left-[calc(12%_-_130px)] top-[calc(72%_-_130px)] h-[680px] w-[1160px]", rgb: "94, 234, 212", opacity: 0.34 },
];

const authBlobs = [
  { pos: "right-[-226px] top-[-226px] h-[740px] w-[820px]", rgb: "125, 211, 252", opacity: 0.5 },
  { pos: "right-[-290px] top-[calc(18%_-_130px)] h-[980px] w-[1080px]", rgb: "20, 184, 166", opacity: 0.42 },
  { pos: "right-[calc(4%_-_130px)] bottom-[calc(-8%_-_130px)] h-[720px] w-[880px]", rgb: "251, 146, 60", opacity: 0.26 },
  { pos: "left-[-290px] bottom-[calc(-10%_-_130px)] h-[680px] w-[960px]", rgb: "253, 186, 116", opacity: 0.42 },
];

const homeFields = [
  { pos: "top-[10%] left-[1%]", cols: 6, rows: 4, size: 84, seed: 13 },
  { pos: "top-[25%] right-[1%]", cols: 6, rows: 4, size: 88, seed: 21 },
  { pos: "top-[41%] left-[2%]", cols: 6, rows: 4, size: 86, seed: 34 },
  { pos: "top-[57%] right-[2%]", cols: 6, rows: 4, size: 84, seed: 47 },
  { pos: "top-[73%] left-[1%]", cols: 6, rows: 4, size: 88, seed: 55 },
  { pos: "top-[87%] right-[1%]", cols: 6, rows: 4, size: 84, seed: 68 },
  { pos: "bottom-[2%] left-1/2 -translate-x-1/2", cols: 10, rows: 3, size: 82, seed: 79 },
];

const pageFields = [
  { pos: "top-[6%] left-[1%] opacity-55", cols: 5, rows: 3, size: 80, seed: 101 },
  { pos: "top-[30%] right-[1%] opacity-55", cols: 5, rows: 3, size: 82, seed: 112 },
  { pos: "top-[56%] left-[1%] opacity-55", cols: 5, rows: 3, size: 80, seed: 123 },
  { pos: "top-[80%] right-[1%] opacity-55", cols: 5, rows: 3, size: 82, seed: 134 },
];

const authFields = [
  { pos: "top-[8%] right-[4%] lg:right-[8%] opacity-85", cols: 7, rows: 5, size: 88, seed: 201 },
  { pos: "bottom-[4%] left-[4%] lg:left-[8%] opacity-75", cols: 7, rows: 3, size: 84, seed: 215 },
];

const homePills = [
  "left-[4%] top-[18%] hidden h-[96px] w-[260px] -rotate-12 rounded-full opacity-65 lg:block",
  "right-[4%] top-[48%] hidden h-[108px] w-[280px] rotate-12 rounded-full opacity-60 lg:block",
  "left-[5%] top-[66%] hidden h-[90px] w-[240px] rotate-6 rounded-full opacity-60 lg:block",
  "right-[5%] top-[81%] hidden h-[100px] w-[250px] -rotate-6 rounded-full opacity-65 lg:block",
];

const authPills = [
  "right-[10%] top-[22%] hidden h-[140px] w-[360px] -rotate-12 rounded-full opacity-75 lg:block",
  "right-[6%] bottom-[16%] hidden h-[120px] w-[320px] rotate-6 rounded-full opacity-70 lg:block",
];

const mode = computed(() => props.variant ?? "home");
const blobs = computed(() => ({ home: homeBlobs, page: pageBlobs, auth: authBlobs })[mode.value]);
const fields = computed(() => ({ home: homeFields, page: pageFields, auth: authFields })[mode.value]);
const pills = computed(() => (mode.value === "home" ? homePills : mode.value === "auth" ? authPills : []));
</script>

<template>
  <div
    class="pointer-events-none absolute inset-0 z-0 overflow-hidden"
    style="contain: layout style paint;"
    aria-hidden="true"
  >
    <div :class="mode === 'auth' ? 'max-lg:opacity-50' : ''">
      <div
        v-for="(b, i) in blobs"
        :key="'b' + i"
        class="absolute rounded-full"
        :class="b.pos"
        :style="blobStyle(b.rgb, b.opacity)"
      ></div>
    </div>

    <div v-if="mode === 'page'" class="absolute inset-0 vt-grain"></div>
    <template v-else>
      <div class="absolute inset-0 vt-dots"></div>
      <div class="absolute inset-0 opacity-70">
        <div class="absolute inset-0 vt-grain"></div>
      </div>
    </template>

    <GlassTileField
      v-for="(f, i) in fields"
      :key="mode + '-f-' + i"
      :cols="f.cols"
      :rows="f.rows"
      :size="f.size"
      :seed="f.seed"
      :mask="softMask"
      variant="mixed"
      class="absolute"
      :class="f.pos"
      style="content-visibility: auto; contain-intrinsic-size: 520px 360px;"
    />

    <div v-for="(p, i) in pills" :key="mode + '-p-' + i" class="vt-glass-pill absolute" :class="p"></div>
    <LandingFloatingIcons v-if="mode === 'home'" />
  </div>
</template>
