<script setup lang="ts">
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import { ToastContainer } from "./components/common";
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white text-audyr-ink font-sans tracking-tight">
    <Navbar />
    <main class="flex-grow">
      <router-view />
    </main>
    <Footer />
    <ToastContainer />
  </div>
</template>
