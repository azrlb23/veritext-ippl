<script setup lang="ts">
defineProps<{ tierId: number }>();
</script>

<template>
  <div class="relative h-[150px] sm:h-[168px] w-full overflow-hidden rounded-2xl border border-[#EFEAF8] bg-gradient-to-br from-[#FDF6EE] via-[#FBF9FF] to-[#EEF1FC]">
    <svg v-if="tierId === 0" viewBox="0 0 420 180" fill="none" aria-hidden="true" class="h-full w-full">
      <defs>
        <linearGradient id="vt-lex-grad" x1="20" y1="0" x2="400" y2="180" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7A2FD6" stop-opacity="0.88" />
          <stop offset="58%" stop-color="#9B4FE6" stop-opacity="0.72" />
          <stop offset="100%" stop-color="#FB923C" stop-opacity="0.85" />
        </linearGradient>
      </defs>
      <g stroke="#C9A0F0" stroke-opacity="0.28" stroke-width="1">
        <line x1="0" y1="36" x2="420" y2="36" /><line x1="0" y1="72" x2="420" y2="72" />
        <line x1="0" y1="108" x2="420" y2="108" /><line x1="0" y1="144" x2="420" y2="144" />
        <line x1="70" y1="0" x2="70" y2="180" /><line x1="140" y1="0" x2="140" y2="180" />
        <line x1="210" y1="0" x2="210" y2="180" /><line x1="280" y1="0" x2="280" y2="180" />
        <line x1="350" y1="0" x2="350" y2="180" />
      </g>
      <line x1="42" y1="52" x2="238" y2="52" stroke="url(#vt-lex-grad)" stroke-width="3" stroke-linecap="round" />
      <line x1="70" y1="72" x2="312" y2="72" stroke="#7A2FD6" stroke-opacity="0.78" stroke-width="2.4" stroke-linecap="round" />
      <line x1="108" y1="92" x2="294" y2="92" stroke="#FB923C" stroke-opacity="0.72" stroke-width="2.2" stroke-linecap="round" />
      <line x1="140" y1="112" x2="368" y2="112" stroke="#8FA8F5" stroke-opacity="0.82" stroke-width="2.6" stroke-linecap="round" />
      <line x1="56" y1="132" x2="210" y2="132" stroke="#9B4FE6" stroke-opacity="0.78" stroke-width="2" stroke-linecap="round" />
      <circle cx="140" cy="72" r="7" fill="#9B4FE6" fill-opacity="0.2" />
      <circle cx="140" cy="72" r="3.4" fill="#7A2FD6" />
      <circle cx="280" cy="112" r="8" fill="#8FA8F5" fill-opacity="0.28" />
      <circle cx="280" cy="112" r="3.6" fill="#7A2FD6" />
      <circle cx="210" cy="52" r="6" fill="#F59E0B" fill-opacity="0.26" />
      <circle cx="210" cy="52" r="3" fill="#FB923C" />
      <circle cx="176" cy="92" r="5" fill="#FB923C" fill-opacity="0.24" />
      <circle cx="176" cy="92" r="2.6" fill="#F59E0B" />
    </svg>

    <svg v-else-if="tierId === 1" viewBox="0 0 420 180" fill="none" aria-hidden="true" class="h-full w-full">
      <defs>
        <linearGradient id="vt-wave-a" x1="0" y1="0" x2="420" y2="180" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7A2FD6" stop-opacity="0.85" />
          <stop offset="55%" stop-color="#9B4FE6" stop-opacity="0.7" />
          <stop offset="100%" stop-color="#8FA8F5" stop-opacity="0.8" />
        </linearGradient>
        <linearGradient id="vt-wave-b" x1="420" y1="0" x2="0" y2="180" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FB923C" stop-opacity="0.72" />
          <stop offset="50%" stop-color="#8FA8F5" stop-opacity="0.65" />
          <stop offset="100%" stop-color="#7A2FD6" stop-opacity="0.48" />
        </linearGradient>
      </defs>
      <path d="M-24 128 C 68 38, 168 158, 258 76 C 324 16, 376 62, 444 28" stroke="url(#vt-wave-a)" stroke-width="2.4" stroke-linecap="round" />
      <path d="M-18 144 C 76 52, 178 168, 266 88 C 334 26, 384 74, 446 42" stroke="#9B4FE6" stroke-opacity="0.52" stroke-width="1.8" stroke-linecap="round" />
      <path d="M-12 160 C 86 68, 186 176, 276 98 C 344 40, 392 86, 448 56" stroke="#8FA8F5" stroke-opacity="0.68" stroke-width="1.6" stroke-linecap="round" />
      <path d="M-28 96 C 58 14, 152 130, 246 52 C 314 -4, 372 44, 442 12" stroke="url(#vt-wave-b)" stroke-width="2" stroke-linecap="round" />
      <path d="M-20 112 C 62 24, 160 144, 252 64 C 320 6, 374 52, 442 20" stroke="#FB923C" stroke-opacity="0.62" stroke-width="1.5" stroke-linecap="round" />
      <path d="M-8 172 C 98 84, 198 182, 286 110 C 352 54, 400 98, 452 72" stroke="#7A2FD6" stroke-opacity="0.32" stroke-width="1.2" stroke-linecap="round" />
      <circle cx="152" cy="96" r="5" fill="#F59E0B" fill-opacity="0.22" />
      <circle cx="152" cy="96" r="2.6" fill="#F59E0B" />
      <circle cx="258" cy="76" r="5.5" fill="#FB923C" fill-opacity="0.25" />
      <circle cx="258" cy="76" r="2.8" fill="#FB923C" />
    </svg>

    <svg v-else-if="tierId === 2" viewBox="0 0 420 180" fill="none" aria-hidden="true" class="h-full w-full">
      <defs>
        <linearGradient id="vt-sty-grad" x1="0" y1="90" x2="420" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#8FA8F5" stop-opacity="0.75" />
          <stop offset="50%" stop-color="#7A2FD6" stop-opacity="0.9" />
          <stop offset="100%" stop-color="#FB923C" stop-opacity="0.78" />
        </linearGradient>
      </defs>
      <path d="M-10 92 Q 35 32, 80 92 T 170 92 T 260 92 T 350 92 T 430 92" stroke="url(#vt-sty-grad)" stroke-width="2.4" stroke-linecap="round" />
      <path d="M-10 92 C 45 148, 95 28, 152 92 C 208 156, 268 30, 326 92 C 368 136, 402 68, 434 92" stroke="#9B4FE6" stroke-opacity="0.64" stroke-width="1.8" stroke-linecap="round" />
      <path d="M-10 104 Q 24 68, 58 104 T 126 104 T 194 104 T 262 104 T 330 104 T 398 104 T 434 104" stroke="#8FA8F5" stroke-opacity="0.72" stroke-width="1.5" stroke-linecap="round" />
      <path d="M-10 78 C 72 138, 148 16, 224 84 C 296 146, 358 26, 434 78" stroke="#FB923C" stroke-opacity="0.68" stroke-width="1.6" stroke-linecap="round" />
      <circle cx="35" cy="62" r="3.4" fill="#7A2FD6" />
      <circle cx="125" cy="122" r="3.2" fill="#F59E0B" />
      <circle cx="215" cy="62" r="6.5" fill="#7A2FD6" fill-opacity="0.2" />
      <circle cx="215" cy="62" r="3.4" fill="#7A2FD6" />
      <circle cx="305" cy="122" r="3.2" fill="#8FA8F5" />
      <circle cx="395" cy="62" r="3.4" fill="#FB923C" />
    </svg>

    <svg v-else viewBox="0 0 420 180" fill="none" aria-hidden="true" class="h-full w-full">
      <defs>
        <radialGradient id="vt-conv-glow" cx="290" cy="88" r="68" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#7A2FD6" stop-opacity="0.34" />
          <stop offset="55%" stop-color="#FB923C" stop-opacity="0.16" />
          <stop offset="100%" stop-color="#8FA8F5" stop-opacity="0" />
        </radialGradient>
      </defs>
      <circle cx="290" cy="88" r="68" fill="url(#vt-conv-glow)" />
      <path d="M-16 34 C 98 34, 198 62, 290 88" stroke="#7A2FD6" stroke-opacity="0.78" stroke-width="2.2" stroke-linecap="round" />
      <path d="M-16 88 C 96 88, 192 88, 290 88" stroke="#FB923C" stroke-opacity="0.74" stroke-width="2" stroke-linecap="round" />
      <path d="M-16 144 C 102 144, 198 116, 290 88" stroke="#8FA8F5" stroke-opacity="0.8" stroke-width="2.2" stroke-linecap="round" />
      <path d="M132 184 C 188 148, 240 116, 290 88" stroke="#9B4FE6" stroke-opacity="0.72" stroke-width="1.8" stroke-linecap="round" />
      <path d="M432 24 C 384 44, 336 66, 290 88" stroke="#F59E0B" stroke-opacity="0.65" stroke-width="1.8" stroke-linecap="round" />
      <path d="M432 152 C 382 132, 336 110, 290 88" stroke="#8FA8F5" stroke-opacity="0.65" stroke-width="1.8" stroke-linecap="round" />
      <circle cx="290" cy="88" r="34" stroke="#FB923C" stroke-opacity="0.48" stroke-width="1.4" />
      <circle cx="290" cy="88" r="20" stroke="#9B4FE6" stroke-opacity="0.65" stroke-width="1.6" />
      <circle cx="290" cy="88" r="7" fill="#7A2FD6" />
      <circle cx="290" cy="88" r="3" fill="#F59E0B" />
    </svg>

    <div
      class="pointer-events-none absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-[#FBF9FF]/85 via-transparent to-transparent"
      aria-hidden="true"
    />
  </div>
</template>
