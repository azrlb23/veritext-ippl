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
      <header class="mx-auto flex w-full max-w-[460px] items-center justify-between gap-6 lg:mx-0">
        <router-link
          to="/"
          class="inline-flex h-11 items-center rounded-full text-[20px] font-semibold tracking-[-0.03em] text-[#14111C] select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        >
          VeriText <span class="ml-1 text-[#8A3FE0]">AI</span>
        </router-link>
        <router-link
          to="/verify"
          class="inline-flex h-11 items-center rounded-full px-4 text-[14px] font-medium text-[#4B4757] transition-colors duration-200 hover:bg-[#14111C]/[0.05] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        >
          Verifikasi sertifikat
        </router-link>
      </header>

      <div class="mx-auto my-6 w-full max-w-[460px] rounded-[36px] bg-white p-6 shadow-float sm:p-10 lg:mx-0">
        <p v-if="eyebrow" class="mb-3 text-[14px] font-medium text-[#5E5A6B]">{{ eyebrow }}</p>
        <h1 class="text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[44px]">
          {{ title }}
          <span v-if="titleAccent" class="vt-accent block pb-1">{{ titleAccent }}</span>
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
