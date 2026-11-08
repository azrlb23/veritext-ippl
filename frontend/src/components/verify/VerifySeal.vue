<script setup lang="ts">
// Stempel "terverifikasi" berwarna penuh, tanpa garis tepi.
</script>

<template>
  <svg class="h-[104px] w-[104px] rotate-[10deg] drop-shadow-[0_14px_20px_rgba(122,47,214,0.35)]" viewBox="0 0 120 120" role="img" aria-label="Stempel sertifikat terverifikasi">
    <defs>
      <linearGradient id="sealFill" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#9B4FE6" /><stop offset="1" stop-color="#6D28D9" />
      </linearGradient>
      <path id="sealArc" d="M60 60 m-43 0 a43 43 0 1 1 86 0 a43 43 0 1 1 -86 0" />
    </defs>
    <circle cx="60" cy="60" r="56" fill="url(#sealFill)" />
    <text font-family="'Plus Jakarta Sans', sans-serif" font-size="9.5" font-weight="600" letter-spacing="2.4" fill="#FFFFFF" fill-opacity="0.85">
      <textPath href="#sealArc">VERITEXT AI SERTIFIKAT ASLI</textPath>
    </text>
    <circle cx="60" cy="60" r="29" fill="#FFFFFF" fill-opacity="0.16" />
    <path d="M45 61 L55 71 L76 49" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>
