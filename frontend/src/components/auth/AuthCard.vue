<script setup lang="ts">
import AuthIllustration from "./AuthIllustration.vue";

interface Props {
  eyebrow?: string;
  title: string;
  subtitle?: string | string[];
}

withDefaults(defineProps<Props>(), {
  eyebrow: "",
  subtitle: "",
});
</script>

<template>
  <div class="min-h-screen w-full flex flex-col lg:flex-row bg-[#FAFBFF] relative overflow-x-hidden font-sans">
    
    <!-- Left Column: Full-Height Form Area (Isolated Layer) -->
    <div class="w-full lg:w-[50%] xl:w-[48%] min-h-screen flex flex-col justify-between px-6 sm:px-12 lg:px-16 xl:px-24 py-8 lg:py-10 bg-white relative z-10 border-r border-[#E8ECF3] shadow-[4px_0_24px_rgba(11,15,25,0.02)]">
      
      <!-- Top Header / Brand -->
      <header class="flex items-center space-x-10 w-full max-w-[420px] mx-auto lg:mx-0">
        <router-link to="/" class="text-[17px] font-bold text-[#0B0F19] tracking-tight font-sans select-none flex items-center">
          VeriText AI
        </router-link>
        <div class="flex items-center space-x-7 text-[14px] font-semibold text-[#5B6475]">
          <router-link to="/verify" class="hover:text-[#0B0F19] transition-colors">
            Verifikasi
          </router-link>
          <a href="#bantuan" class="hover:text-[#0B0F19] transition-colors">
            Bantuan
          </a>
        </div>
      </header>

      <!-- Center Form Container -->
      <div class="w-full max-w-[400px] mx-auto my-auto py-8">
        <!-- Eyebrow & Title -->
        <div class="space-y-1.5 mb-2">
          <p v-if="eyebrow" class="text-[13px] font-bold tracking-[0.5px] text-[#5B6475] uppercase">
            {{ eyebrow }}
          </p>
          <h1 class="text-[34px] sm:text-[40px] font-semibold tracking-[-0.8px] text-[#0B0F19] leading-[1.12] font-sans">
            {{ title }}
          </h1>
        </div>

        <!-- Subtitle -->
        <div v-if="subtitle" class="text-[14.5px] font-normal leading-[22px] text-[#5B6475] mb-5">
          <template v-if="Array.isArray(subtitle)">
            <p v-for="(line, idx) in subtitle" :key="idx">{{ line }}</p>
          </template>
          <template v-else>
            <p>{{ subtitle }}</p>
          </template>
        </div>

        <!-- Slot Form Content -->
        <div class="w-full">
          <slot />
        </div>
      </div>

      <!-- Bottom Micro-footer -->
      <footer class="w-full max-w-[420px] mx-auto lg:mx-0 pt-4 text-[12px] text-[#8E98AB] flex items-center justify-between">
        <span>&copy; {{ new Date().getFullYear() }} VeriText AI</span>
        <span>Audit orisinalitas naskah</span>
      </footer>

    </div>

    <!-- Right Column: Full-Height Aurora Glass Artwork (GPU Accelerated & Isolated) -->
    <div
      class="hidden lg:flex lg:w-[50%] xl:w-[52%] min-h-screen relative overflow-hidden bg-gradient-to-br from-[#E8F0FF] via-[#DDF4FF] to-[#EDE7FF] items-center justify-center select-none transform-gpu will-change-transform"
      style="content-visibility: auto; contain: strict;"
    >
      <!-- Hardware-accelerated CSS Aurora Mesh (Zero CPU Blur Overhead) -->
      <div
        class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_75%_55%_at_85%_15%,rgba(59,130,246,0.32),transparent_70%),radial-gradient(ellipse_75%_55%_at_15%_85%,rgba(34,211,238,0.28),transparent_70%),radial-gradient(circle_at_50%_50%,rgba(167,139,250,0.25),transparent_65%)]"
      ></div>

      <!-- Vector Glass Refraction Illustration -->
      <AuthIllustration />
    </div>

  </div>
</template>
