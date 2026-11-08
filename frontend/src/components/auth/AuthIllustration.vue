<script setup lang="ts">
// Ilustrasi pita kaca aurora - High-Performance GPU-Accelerated Vector Art
</script>

<template>
  <div class="w-full h-full relative select-none overflow-hidden pointer-events-none">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="690 78 430 740"
      preserveAspectRatio="xMidYMid slice"
      class="w-full h-full absolute inset-0"
    >
      <defs>
        <!-- High-Performance GPU Gradients -->
        <radialGradient id="gOrb" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stop-color="#3B5BDB" stop-opacity="0.95" />
          <stop offset="0.65" stop-color="#1A73D9" stop-opacity="0.8" />
          <stop offset="0.88" stop-color="#3B82F6" stop-opacity="0.25" />
          <stop offset="1" stop-color="#3B82F6" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="gCyan" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stop-color="#22D3EE" stop-opacity="0.75" />
          <stop offset="0.5" stop-color="#22D3EE" stop-opacity="0.4" />
          <stop offset="1" stop-color="#22D3EE" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="gViolet" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stop-color="#A78BFA" stop-opacity="0.7" />
          <stop offset="0.55" stop-color="#A78BFA" stop-opacity="0.35" />
          <stop offset="1" stop-color="#A78BFA" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="gBand" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22" />
          <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.04" />
          <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.10" />
        </linearGradient>

        <clipPath id="cardClip"><rect x="690" y="78" width="430" height="740" /></clipPath>
        <clipPath id="band0"><rect x="690" y="78" width="110" height="740" /></clipPath>
        <clipPath id="band1"><rect x="800" y="78" width="110" height="740" /></clipPath>
        <clipPath id="band2"><rect x="910" y="78" width="110" height="740" /></clipPath>
        <clipPath id="band3"><rect x="1020" y="78" width="100" height="740" /></clipPath>
      </defs>

      <g clip-path="url(#cardClip)">
        <!-- Band 0 -->
        <g clip-path="url(#band0)">
          <g transform="translate(846 456) scale(0.94) translate(-880 -448)">
            <circle cx="880" cy="448" r="238" fill="url(#gOrb)" />
            <circle cx="770" cy="330" r="100" fill="url(#gCyan)" />
            <circle cx="990" cy="640" r="130" fill="url(#gViolet)" />
          </g>
        </g>
        <rect x="690" y="78" width="110" height="740" fill="url(#gBand)" />
        <rect x="690" y="78" width="2" height="740" fill="#FFFFFF" fill-opacity="0.55" />

        <!-- Band 1 -->
        <g clip-path="url(#band1)">
          <g transform="translate(868 451) scale(0.99) translate(-880 -448)">
            <circle cx="880" cy="448" r="238" fill="url(#gOrb)" />
            <circle cx="770" cy="330" r="100" fill="url(#gCyan)" />
            <circle cx="990" cy="640" r="130" fill="url(#gViolet)" />
          </g>
        </g>
        <rect x="800" y="78" width="110" height="740" fill="url(#gBand)" />
        <rect x="800" y="78" width="2" height="740" fill="#FFFFFF" fill-opacity="0.55" />

        <!-- Band 2 -->
        <g clip-path="url(#band2)">
          <g transform="translate(892 445) scale(1.04) translate(-880 -448)">
            <circle cx="880" cy="448" r="238" fill="url(#gOrb)" />
            <circle cx="770" cy="330" r="100" fill="url(#gCyan)" />
            <circle cx="990" cy="640" r="130" fill="url(#gViolet)" />
          </g>
        </g>
        <rect x="910" y="78" width="110" height="740" fill="url(#gBand)" />
        <rect x="910" y="78" width="2" height="740" fill="#FFFFFF" fill-opacity="0.55" />

        <!-- Band 3 -->
        <g clip-path="url(#band3)">
          <g transform="translate(916 440) scale(1.1) translate(-880 -448)">
            <circle cx="880" cy="448" r="238" fill="url(#gOrb)" />
            <circle cx="770" cy="330" r="100" fill="url(#gCyan)" />
            <circle cx="990" cy="640" r="130" fill="url(#gViolet)" />
          </g>
        </g>
        <rect x="1020" y="78" width="100" height="740" fill="url(#gBand)" />
        <rect x="1020" y="78" width="2" height="740" fill="#FFFFFF" fill-opacity="0.55" />
      </g>

      <!-- Wordmark dan 3 Pilar Label -->
      <text x="886" y="464" font-size="46" font-weight="600" letter-spacing="1" fill="#FFFFFF" text-anchor="middle" font-family="'Outfit','Plus Jakarta Sans',sans-serif">
        VeriText AI
      </text>

      <text x="900" y="318" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">Tiga tier</text>
      <text x="900" y="334" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">pemeriksaan</text>

      <text x="752" y="566" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">Laporan per</text>
      <text x="752" y="582" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">kalimat</text>

      <text x="968" y="548" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">Sertifikat</text>
      <text x="968" y="564" font-size="12.5" fill="#FFFFFF" font-family="'Outfit','Plus Jakarta Sans',sans-serif">terverifikasi QR</text>
    </svg>
  </div>
</template>
