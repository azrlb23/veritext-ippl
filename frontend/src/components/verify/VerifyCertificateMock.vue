<script setup lang="ts">
// Ilustrasi lembar sertifikat dengan kode QR. Data contoh, bukan sertifikat nyata.
const SIZE = 17;

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const origins = [[0, 0], [SIZE - 7, 0], [0, SIZE - 7]];

function finderCell(x: number, y: number): boolean | null {
  for (const [ox, oy] of origins) {
    if (x >= ox && x < ox + 7 && y >= oy && y < oy + 7) {
      const lx = x - ox;
      const ly = y - oy;
      return lx === 0 || lx === 6 || ly === 0 || ly === 6 || (lx >= 2 && lx <= 4 && ly >= 2 && ly <= 4);
    }
  }
  return null;
}

const nearFinder = (x: number, y: number) => origins.some(([ox, oy]) => x >= ox - 1 && x <= ox + 7 && y >= oy - 1 && y <= oy + 7);

const rand = seeded(5);
const cells: { x: number; y: number }[] = [];
for (let y = 0; y < SIZE; y++) {
  for (let x = 0; x < SIZE; x++) {
    const finder = finderCell(x, y);
    if (finder === true || (finder === null && !nearFinder(x, y) && rand() > 0.52)) cells.push({ x, y });
  }
}
</script>

<template>
  <div
    class="w-[290px] -rotate-2 rounded-[28px] bg-white p-6 shadow-float lg:[transform:perspective(1200px)_rotateY(14deg)_rotateZ(-4deg)]"
    aria-hidden="true"
  >
    <div class="text-[12px] font-medium text-[#5E5A6B]">Sertifikat hasil audit orisinalitas</div>
    <div class="mt-1 text-[15px] font-semibold text-[#14111C]">Naskah-Laporan-2026.pdf</div>

    <div class="mt-5 flex items-center justify-between gap-3">
      <div class="relative shrink-0 p-3">
        <svg class="h-[104px] w-[104px]" viewBox="0 0 17 17" shape-rendering="crispEdges">
          <rect v-for="(c, i) in cells" :key="i" :x="c.x" :y="c.y" width="1" height="1" fill="#14111C" />
        </svg>
        <span class="absolute left-0 top-0 h-5 w-5 rounded-tl-[8px] border-l-[3px] border-t-[3px] border-[#8A3FE0]"></span>
        <span class="absolute right-0 top-0 h-5 w-5 rounded-tr-[8px] border-r-[3px] border-t-[3px] border-[#8A3FE0]"></span>
        <span class="absolute bottom-0 left-0 h-5 w-5 rounded-bl-[8px] border-b-[3px] border-l-[3px] border-[#8A3FE0]"></span>
        <span class="absolute bottom-0 right-0 h-5 w-5 rounded-br-[8px] border-b-[3px] border-r-[3px] border-[#8A3FE0]"></span>
      </div>
      <div>
        <div class="text-[38px] font-semibold leading-none tracking-[-0.05em] text-[#14111C]">88%</div>
        <div class="mt-1 text-[12px] text-[#5E5A6B]">Skor orisinalitas</div>
      </div>
    </div>

    <div class="mt-5 rounded-[14px] bg-[#F3EEFA] px-3 py-2 font-mono text-[10.5px] leading-[1.5] text-[#4B4757]">
      8f2a91c4-b7e1-4d90-a35c-7e6189df0123
    </div>
  </div>
</template>
