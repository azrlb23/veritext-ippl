<script setup lang="ts">
import { onMounted } from "vue";
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import { ToastContainer } from "./components/common";
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();
onMounted(() => {
  if (authStore.isAuthenticated) {
    void authStore.fetchProfile();
  }
});
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white text-audyr-ink font-sans tracking-tight">
    <Navbar />
    <main class="flex-grow pt-20 sm:pt-24">
      <router-view />
    </main>
    <Footer />
    <ToastContainer />
  </div>
</template>
