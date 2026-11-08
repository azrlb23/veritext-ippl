<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { getSegmentedNavLinks } from "../utils/navigation";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const isMobileMenuOpen = ref(false);

const userDisplayName = computed(() => authStore.user?.full_name || "Pengguna");
const userInitial = computed(() => authStore.user?.full_name?.charAt(0).toUpperCase() || "U");
const isGuest = computed(() => !authStore.isAuthenticated);
const isSuperAdmin = computed(() => authStore.isAuthenticated && (authStore.role === "ADMIN" || Boolean(authStore.isAdmin)));
const navLinks = computed(() => getSegmentedNavLinks(authStore.isAuthenticated, authStore.role));

function isItemActive(to: string): boolean {
  if (to.includes("#")) {
    const [p, h] = to.split("#");
    return route.path === p && route.hash === `#${h}`;
  }
  if (to === "/admin") return route.path === "/admin" && (!route.hash || route.hash === "#overview");
  return to === "/" ? route.path === "/" : route.path.startsWith(to);
}

const closeMenu = () => {
  isMobileMenuOpen.value = false;
};
watch(() => [route.path, route.hash], closeMenu);

async function handleLogout() {
  closeMenu();
  await authStore.logout();
  showNotification("Anda telah berhasil keluar dari akun.", "info", "Sesi Berakhir");
  router.push("/login");
}
</script>

<template>
  <header class="fixed top-6 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none select-none">
    <div
      class="pointer-events-auto w-full max-w-[1060px] bg-white/80 backdrop-blur-xl shadow-lift transition-all duration-200"
      :class="isMobileMenuOpen ? 'rounded-[28px] px-6 py-4 flex flex-col' : 'h-[68px] rounded-[34px] px-6 md:px-9 flex items-center justify-between'"
    >
      <div class="flex items-center justify-between w-full" :class="{ 'h-[44px]': isMobileMenuOpen, 'h-full': !isMobileMenuOpen }">
        <router-link :to="isSuperAdmin ? '/admin' : '/'" class="flex items-center rounded-full flex-shrink-0" @click="closeMenu">
          <span class="text-[20px] font-semibold text-[#14111C]">VeriText <span class="text-[#8A3FE0]">AI</span></span>
        </router-link>

        <nav class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="whitespace-nowrap transition-colors rounded-[26px] text-[15px] font-medium inline-flex items-center justify-center"
            :class="isItemActive(item.to) ? 'h-[52px] px-7 bg-[#F3EEFA] text-[#14111C]' : 'px-5 py-2 text-[#5E5A6B] hover:text-[#14111C]'"
          >{{ item.name }}</router-link>
        </nav>

        <div class="flex items-center space-x-2 flex-shrink-0">
          <template v-if="isGuest">
            <div class="hidden md:flex items-center space-x-3">
              <router-link to="/login" class="text-[15px] font-medium text-[#14111C] hover:text-[#8A3FE0] px-4 py-2">Masuk</router-link>
              <router-link to="/register" class="h-[44px] px-7 rounded-[22px] bg-[#14111C] hover:bg-[#2B2438] text-white text-[14.5px] font-semibold inline-flex items-center justify-center shadow-btn-dark transition-colors">Daftar</router-link>
            </div>
          </template>
          <template v-else>
            <div class="hidden md:flex items-center">
              <div class="h-[52px] pl-3.5 pr-5 rounded-[26px] bg-[#F3EEFA] flex items-center space-x-3">
                <div class="w-7 h-7 rounded-full bg-white text-[#14111C] text-[13px] font-semibold flex items-center justify-center shadow-sm">{{ userInitial }}</div>
                <span class="text-[15px] font-medium text-[#14111C] truncate max-w-[115px]">{{ userDisplayName }}</span>
                <span v-if="!isSuperAdmin" class="text-[14px] font-semibold text-[#6D28D9] tabular-nums pl-1">{{ authStore.tokenBalance }}T</span>
              </div>
              <button type="button" @click="handleLogout" class="text-[15px] font-medium text-[#5E5A6B] hover:text-[#14111C] pl-3">Keluar</button>
            </div>
          </template>

          <button
            type="button"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="md:hidden p-2 rounded-full text-[#5E5A6B] hover:text-[#14111C] hover:bg-[#F3EEFA]"
            aria-label="Toggle menu navigasi"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="isMobileMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Dropdown Navigation Drawer -->
      <div v-if="isMobileMenuOpen" class="md:hidden pt-4 pb-2 border-t border-[#14111C]/[0.06] mt-3 space-y-3">
        <nav class="flex flex-col space-y-1">
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="px-4 py-2.5 rounded-[16px] text-[15px] font-medium transition-colors"
            :class="isItemActive(item.to) ? 'bg-[#F3EEFA] text-[#14111C]' : 'text-[#5E5A6B] hover:text-[#14111C] hover:bg-[#F3EEFA]/60'"
            @click="closeMenu"
          >{{ item.name }}</router-link>
        </nav>
        <div class="pt-3 border-t border-[#14111C]/[0.06] flex items-center justify-between">
          <template v-if="isGuest">
            <router-link to="/login" class="text-[15px] font-medium text-[#14111C] hover:text-[#8A3FE0] px-3 py-1.5" @click="closeMenu">Masuk</router-link>
            <router-link to="/register" class="h-[40px] px-5 rounded-[20px] bg-[#14111C] hover:bg-[#2B2438] text-white text-[14px] font-semibold inline-flex items-center justify-center shadow-btn-dark transition-colors" @click="closeMenu">Daftar</router-link>
          </template>
          <template v-else>
            <div class="flex items-center space-x-2.5">
              <div class="w-7 h-7 rounded-full bg-white text-[#14111C] text-[13px] font-semibold flex items-center justify-center shadow-sm">{{ userInitial }}</div>
              <span class="text-[14.5px] font-medium text-[#14111C] truncate max-w-[120px]">{{ userDisplayName }}</span>
              <span v-if="!isSuperAdmin" class="text-[13.5px] font-semibold text-[#6D28D9] tabular-nums pl-1">({{ authStore.tokenBalance }}T)</span>
            </div>
            <button type="button" @click="handleLogout" class="text-[14.5px] font-medium text-[#5E5A6B] hover:text-[#14111C] px-2 py-1">Keluar</button>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
