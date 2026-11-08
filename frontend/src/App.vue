<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import LandingBackdrop from "./components/landing/LandingBackdrop.vue";
import { ToastContainer, WelcomeModal } from "./components/common";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const authStore = useAuthStore() as ReturnType<typeof useAuthStore> & {
  welcomeName?: string | null;
  consumeWelcome?: () => void;
};

// Halaman autentikasi bersifat standalone (tanpa navbar capsule & footer global).
const isStandalonePage = computed(() => {
  return (
    Boolean(route.meta.isStandalone) ||
    route.path.startsWith("/login") ||
    route.path.startsWith("/register") ||
    route.path.startsWith("/forgot-password") ||
    route.path.startsWith("/reset-password") ||
    route.path.startsWith("/onboarding") ||
    route.path.startsWith("/auth/callback")
  );
});

const backdropVariant = computed(() => route.meta.backdrop);
const isLanding = computed(() => Boolean(backdropVariant.value));

const isWelcomeOpen = computed(() => {
  return Boolean(authStore.welcomeName) && !isStandalonePage.value;
});

function handleCloseWelcome() {
  if (typeof authStore.consumeWelcome === "function") {
    authStore.consumeWelcome();
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    void authStore.fetchProfile();
  }
});
</script>

<template>
  <div
    class="flex flex-col min-h-screen text-[#0B0F19] font-sans tracking-tight relative"
    :class="[
      isStandalonePage
        ? 'bg-white'
        : isLanding
          ? 'bg-[#F2F2F4]'
          : 'bg-[linear-gradient(135deg,#E8F0FF_0%,#DDF4FF_55%,#EDE7FF_100%)]'
    ]"
  >
    <!-- Soft Ambient Aurora Radial Glows (GPU-accelerated with pointer-events-none) -->
    <div
      v-if="!isStandalonePage && !isLanding"
      class="fixed inset-0 pointer-events-none z-0 overflow-hidden transform-gpu"
      aria-hidden="true"
    >
      <div
        class="absolute -top-[10%] -right-[5%] w-[600px] h-[600px] rounded-full bg-[#3B82F6] opacity-[0.32] blur-[100px] transform-gpu"
      />
      <div
        class="absolute top-[35%] -left-[10%] w-[650px] h-[650px] rounded-full bg-[#22D3EE] opacity-[0.30] blur-[110px] transform-gpu"
      />
      <div
        class="absolute top-[70%] -right-[5%] w-[600px] h-[600px] rounded-full bg-[#A78BFA] opacity-[0.30] blur-[100px] transform-gpu"
      />
    </div>

    <LandingBackdrop v-if="isLanding" :variant="backdropVariant" />

    <Navbar v-if="!isStandalonePage" />
    <main
      :class="[
        isStandalonePage
          ? 'flex-grow min-h-screen p-0'
          : 'flex-grow pt-[92px] relative z-10'
      ]"
    >
      <router-view />
    </main>
    <Footer v-if="!isStandalonePage" class="relative z-10" />
    <ToastContainer />
    <WelcomeModal
      :is-open="isWelcomeOpen"
      :name="authStore.welcomeName || 'Pengguna'"
      :role="authStore.role"
      @close="handleCloseWelcome"
    />
  </div>
</template>
