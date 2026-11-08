<script setup lang="ts">
import VerifyCertificateMock from "./VerifyCertificateMock.vue";
import VerifyPhoneMock from "./VerifyPhoneMock.vue";
</script>

<template>
  <div class="flex flex-col items-center gap-3 lg:my-8 lg:origin-center lg:scale-[1.14] lg:flex-row lg:justify-center lg:gap-4">
    <VerifyCertificateMock />

    <div class="flex flex-col items-center" aria-hidden="true">
      <svg class="h-[100px] w-[70px] lg:hidden" viewBox="0 0 70 100" fill="none">
        <defs>
          <linearGradient id="flowV" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#8A3FE0" /><stop offset="1" stop-color="#D26BE6" />
          </linearGradient>
        </defs>
        <path d="M35 4 C 8 34, 8 64, 35 92" stroke="url(#flowV)" stroke-width="3.5" stroke-linecap="round" />
        <path d="M22 80 L35 94 L48 80" stroke="url(#flowV)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <svg class="hidden h-[80px] w-[150px] lg:block" viewBox="0 0 150 80" fill="none">
        <defs>
          <linearGradient id="flowH" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#8A3FE0" /><stop offset="1" stop-color="#D26BE6" />
          </linearGradient>
        </defs>
        <path d="M4 58 C 40 8, 104 8, 144 44" stroke="url(#flowH)" stroke-width="3.5" stroke-linecap="round" />
        <path d="M128 30 L145 45 L123 52" stroke="url(#flowH)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="text-[12.5px] font-medium text-[#5E5A6B]">Pindai dengan kamera</span>
    </div>

    <VerifyPhoneMock />
  </div>
</template>
