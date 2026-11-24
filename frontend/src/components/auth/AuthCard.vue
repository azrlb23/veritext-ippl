<script setup lang="ts">
import AuthIllustration from "./AuthIllustration.vue";

interface Props {
  eyebrow?: string;
  title: string;
  titleAccent?: string;
  subtitle?: string | string[];
}

withDefaults(defineProps<Props>(), {
  eyebrow: "",
  titleAccent: "",
  subtitle: "",
});
</script>

<template>
  <div class="relative flex min-h-screen w-full flex-col font-sans lg:flex-row">
    <div class="relative z-10 flex min-h-screen w-full flex-col justify-between px-5 py-6 sm:px-12 lg:w-[50%] lg:px-16 lg:py-10 xl:w-[48%] xl:px-24">
      <header class="mx-auto flex w-full max-w-[460px] items-center justify-start gap-6 lg:mx-0">
        <router-link
          to="/"
          aria-label="Kembali ke beranda"
          title="Kembali ke beranda"
          class="group inline-flex h-11 w-11 items-center justify-center rounded-full bg-white text-[#4B4757] shadow-lift transition-all duration-200 hover:text-[#14111C] hover:shadow-float focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        >
          <svg class="h-4 w-4 text-[#5E5A6B] transition-transform duration-200 group-hover:-translate-x-0.5 group-hover:text-[#14111C]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </router-link>
      </header>

      <div class="mx-auto my-6 w-full max-w-[460px] rounded-[36px] bg-white p-6 shadow-float sm:p-9 lg:mx-0">
        <h1 class="text-[26px] font-semibold leading-[1.15] tracking-[-0.03em] text-[#14111C]">
          {{ title }}
          <span v-if="titleAccent" class="text-[#0F766E]">{{ titleAccent }}</span>
        </h1>

        <div v-if="subtitle" class="mt-4 text-[15px] leading-[1.65] text-[#4B4757]">
          <template v-if="Array.isArray(subtitle)">
            <p v-for="(line, idx) in subtitle" :key="idx">{{ line }}</p>
          </template>
          <p v-else>{{ subtitle }}</p>
        </div>

        <div class="mt-7 w-full">
          <slot />
        </div>
      </div>

      <footer class="mx-auto flex w-full max-w-[460px] items-center justify-between pt-4 text-[12.5px] text-[#5E5A6B] lg:mx-0">
        <span>&copy; {{ new Date().getFullYear() }} VeriText AI</span>
        <span>Audit orisinalitas naskah</span>
      </footer>
    </div>

    <div class="relative hidden select-none lg:flex lg:w-[50%] xl:w-[52%]">
      <AuthIllustration />
    </div>
  </div>
</template>
