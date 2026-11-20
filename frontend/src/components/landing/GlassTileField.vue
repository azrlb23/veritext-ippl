<script setup lang="ts">
// Medan ubin kaca dengan variasi bentuk geometris yang memudar ke tepinya sebelum menyentuh batas kontainer.
const props = withDefaults(
  defineProps<{
    cols: number;
    rows: number;
    size?: number;
    seed?: number;
    mask?: string;
    variant?: "tiles" | "mixed";
  }>(),
  {
    size: 96,
    seed: 7,
    variant: "mixed",
    mask: "radial-gradient(ellipse 64% 64% at 50% 50%, #000 0%, #000 22%, transparent 70%)",
  },
);

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const mixedShapes = [
  "rounded-[20px]",
  "rounded-[20px]",
  "rounded-[20px]",
  "rounded-full scale-[0.82]",
  "rounded-full h-[62%] self-center",
  "rounded-[28px] rotate-6 scale-95",
  "rounded-[28px] -rotate-6 scale-95",
];

const rand = seeded(props.seed);
const tiles = Array.from({ length: props.cols * props.rows }, () => {
  const opacity = Number((0.3 + rand() * 0.68).toFixed(2));
  const pick = rand();
  const shape =
    props.variant === "tiles"
      ? "rounded-[20px]"
      : mixedShapes[Math.floor(pick * mixedShapes.length)];
  return { opacity, shape };
});
</script>

<template>
  <div
    class="grid gap-1.5"
    :style="{
      gridTemplateColumns: `repeat(${cols}, ${size}px)`,
      gridAutoRows: `${size}px`,
      WebkitMaskImage: mask,
      maskImage: mask,
      contain: 'layout style paint',
    }"
  >
    <i
      v-for="(tile, i) in tiles"
      :key="i"
      class="vt-tile block"
      :class="tile.shape"
      :style="{ opacity: tile.opacity }"
    ></i>
  </div>
</template>
