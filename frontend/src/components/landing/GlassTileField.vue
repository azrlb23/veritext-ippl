<script setup lang="ts">
// Medan ubin kaca yang memudar ke tepinya (mask), dipakai sebagai bagian latar halaman.
const props = withDefaults(defineProps<{ cols: number; rows: number; size?: number; seed?: number; mask?: string }>(), {
  size: 96,
  seed: 7,
  mask: "radial-gradient(ellipse 70% 70% at 50% 50%, #000 0%, transparent 100%)",
});

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const rand = seeded(props.seed);
const tiles = Array.from({ length: props.cols * props.rows }, () => Number((0.3 + rand() * 0.7).toFixed(2)));
</script>

<template>
  <div
    class="grid gap-1"
    :style="{
      gridTemplateColumns: `repeat(${cols}, ${size}px)`,
      gridAutoRows: `${size}px`,
      WebkitMaskImage: mask,
      maskImage: mask,
    }"
  >
    <i v-for="(o, i) in tiles" :key="i" class="vt-tile" :style="{ opacity: o }"></i>
  </div>
</template>
