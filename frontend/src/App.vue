<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import { ToastContainer } from "./components/common";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const authStore = useAuthStore();

// Sembunyikan capsule navbar publik & consumer footer di konsol tata kelola Admin.
// Konsol admin memiliki persistent left sidebar dan top application bar sendiri (Zendenta style).
const isAdminPortal = computed(() => {
  return (
    route.path.startsWith("/admin") ||
    (route.path.startsWith("/corpus") && authStore.role === "ADMIN")
  );
});

onMounted(() => {
  if (authStore.isAuthenticated) {
    void authStore.fetchProfile();
  }
});
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white text-audyr-ink font-sans tracking-tight">
    <Navbar v-if="!isAdminPortal" />
    <main :class="isAdminPortal ? 'flex-grow min-h-screen p-0 bg-[#f8f9fb]' : 'flex-grow pt-20 sm:pt-24'">
      <router-view />
    </main>
    <Footer v-if="!isAdminPortal" />
    <ToastContainer />
  </div>
</template>
