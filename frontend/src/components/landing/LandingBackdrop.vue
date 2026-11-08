<script setup lang="ts">
// Latar satu halaman penuh untuk beranda: sapuan warna yang menyebar tanpa tepi,
// sehingga seksi-seksi di atasnya menyatu dengan halaman.
const blobs = [
  "-right-32 top-[1%] h-[460px] w-[560px] bg-[#8FA8F5] opacity-60",
  "-left-40 top-[13%] h-[640px] w-[900px] bg-[#8A3FE0] opacity-55",
  "right-[8%] top-[17%] h-[360px] w-[540px] bg-[#D26BE6] opacity-40",
  "-right-40 top-[34%] h-[520px] w-[620px] bg-[#8FA8F5] opacity-40",
  "-left-56 top-[50%] h-[640px] w-[860px] bg-[#8A3FE0] opacity-25",
  "left-[10%] top-[72%] h-[520px] w-[1100px] bg-[#C9A0F0] opacity-45",
  "-right-32 top-[86%] h-[420px] w-[560px] bg-[#8FA8F5] opacity-35",
];
</script>

<template>
  <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
    <div v-for="(b, i) in blobs" :key="i" class="absolute rounded-full blur-[140px]" :class="b"></div>
  </div>
</template>
