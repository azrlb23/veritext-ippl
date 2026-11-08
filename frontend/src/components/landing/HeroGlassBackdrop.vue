<script setup lang="ts">
// Latar hero: garis vertikal sangat tipis di atas dan ubin kaca violet di dasar.
// Keduanya memudar di tepi sehingga menyatu dengan latar halaman.
const COLS = 14;
const ROWS = 5;

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const rand = seeded(11);
const tiles = Array.from({ length: COLS * ROWS }, () => Number((0.35 + rand() * 0.65).toFixed(2)));
</script>

<template>
  <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
    <div class="vt-lines absolute inset-x-0 top-0 h-[70%]"></div>

    <div class="vt-fade-x absolute inset-x-0 bottom-0 h-[560px]">
      <div class="vt-tiles grid h-full gap-[3px]" :style="{ gridTemplateColumns: `repeat(${COLS}, 1fr)` }">
        <i v-for="(o, i) in tiles" :key="i" class="vt-tile" :style="{ opacity: o }"></i>
      </div>
    </div>
  </div>
</template>
