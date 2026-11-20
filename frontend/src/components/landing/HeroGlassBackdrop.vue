<script setup lang="ts">
// Latar hero: medan ubin kaca lebar dan kapsul kaca mengambang dengan masker pudar sebelum tepi kontainer.
import GlassTileField from "./GlassTileField.vue";

const fadeMask =
  "radial-gradient(ellipse 68% 48% at 50% 52%, #000 0%, #000 28%, transparent 68%)";
const fieldMask =
  "radial-gradient(ellipse 64% 62% at 50% 50%, #000 0%, #000 24%, transparent 68%)";
</script>

<template>
  <div
    class="pointer-events-none absolute inset-0 z-0 overflow-hidden"
    style="contain: layout style paint;"
    aria-hidden="true"
  >
    <div
      class="absolute inset-x-0 bottom-0 h-[620px] sm:h-[720px]"
      :style="{ maskImage: fadeMask, WebkitMaskImage: fadeMask }"
    >
      <GlassTileField
        :cols="16"
        :rows="6"
        :size="88"
        :seed="11"
        variant="mixed"
        :mask="fieldMask"
        class="absolute left-1/2 top-[52%] -translate-x-1/2 -translate-y-1/2 opacity-90"
      />

      <div
        class="vt-glass-pill absolute left-[12%] top-[30%] h-[88px] w-[220px] -rotate-12 rounded-full opacity-75 sm:h-[116px] sm:w-[320px]"
      ></div>
      <div
        class="vt-glass-pill absolute right-[12%] top-[34%] h-[84px] w-[200px] rotate-[10deg] rounded-full opacity-70 sm:h-[108px] sm:w-[290px]"
      ></div>
      <div
        class="vt-glass-pill absolute bottom-[24%] left-1/2 h-[78px] w-[260px] -translate-x-1/2 -rotate-6 rounded-full opacity-65 sm:h-[100px] sm:w-[380px]"
      ></div>
    </div>
  </div>
</template>
