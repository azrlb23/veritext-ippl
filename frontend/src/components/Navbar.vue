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
const userInitial = computed(() => {
  if (authStore.user?.full_name) {
    return authStore.user.full_name.charAt(0).toUpperCase();
  }
  return "U";
});

const isGuest = computed(() => !authStore.isAuthenticated);
const isSuperAdmin = computed(() => authStore.isAuthenticated && authStore.role === "ADMIN");
const isReviewer = computed(() => authStore.isAuthenticated && authStore.role === "REVIEWER");

// Navigasi Tengah Tersegmentasi Berdasarkan 4 Kondisi Pengguna
const navLinks = computed(() => getSegmentedNavLinks(authStore.isAuthenticated, authStore.role));

function isItemActive(targetPath: string): boolean {
  if (targetPath.includes("#")) {
    const [pathPart, hashPart] = targetPath.split("#");
    return route.path === pathPart && route.hash === `#${hashPart}`;
  }
  if (targetPath === "/admin") {
    return route.path === "/admin" && (!route.hash || route.hash === "#overview");
  }
  if (targetPath === "/") {
    return route.path === "/";
  }
  if (targetPath.startsWith("/verify")) {
    return route.path.startsWith("/verify");
  }
  return route.path.startsWith(targetPath);
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false;
}

watch(
  () => [route.path, route.hash],
  () => {
    isMobileMenuOpen.value = false;
  }
);

async function handleLogout() {
  closeMobileMenu();
  await authStore.logout();
  showNotification("Anda telah berhasil keluar dari akun.", "info", "Sesi Berakhir");
  router.push("/login");
}
</script>

<template>
  <header class="bg-white border-b border-[#ededed] sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <!-- Brand Logo -->
      <router-link
        :to="isSuperAdmin ? '/admin' : '/'"
        class="flex items-center space-x-2.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] rounded-[4px]"
        @click="closeMobileMenu"
      >
        <div class="w-7 h-7 rounded-[4px] bg-[#262626] flex items-center justify-center text-white font-extrabold text-xs">
          V
        </div>
        <div class="flex items-center">
          <span class="text-base font-extrabold tracking-tight text-[#262626]">
            VeriText<span class="italic font-bold text-[#686868] ml-0.5">AI</span>
          </span>
          <span
            v-if="isSuperAdmin"
            class="hidden sm:inline-block ml-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded-[4px] bg-[#fafafa] text-[#262626] border border-[#ededed] tracking-wider"
          >
            Admin Console
          </span>
          <span
            v-else
            class="hidden sm:inline-block ml-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded-[4px] bg-[#fafafa] text-[#686868] border border-[#ededed] tracking-wider"
          >
            Hybrid Engine
          </span>
        </div>
      </router-link>

      <!-- Desktop Navigation Links (Segmented & Clean Pills) -->
      <nav class="hidden md:flex items-center space-x-1 lg:space-x-1.5 text-xs tracking-tight">
        <router-link
          v-for="item in navLinks"
          :key="item.to"
          :to="item.to"
          class="whitespace-nowrap px-2.5 lg:px-3 py-1.5 rounded-[4px] font-semibold transition-all duration-150 ease-out focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626]"
          :class="[
            isItemActive(item.to)
              ? 'bg-[#262626] text-white font-bold shadow-sm'
              : 'text-[#686868] hover:text-[#262626] hover:bg-[#f5f5f5]',
          ]"
        >
          {{ item.name }}
        </router-link>
      </nav>

      <!-- User Session Actions & Hamburger -->
      <div class="flex items-center space-x-2 flex-shrink-0">
        <!-- Kondisi 1: Tamu (Belum Login / !authStore.isAuthenticated) -->
        <template v-if="isGuest">
          <div class="hidden md:flex items-center space-x-2">
            <router-link
              to="/login"
              class="text-xs font-semibold text-[#686868] hover:text-[#262626] px-3 py-1.5 rounded-[4px] active:scale-[0.98] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626] transition-colors duration-150 ease-out"
            >
              Masuk
            </router-link>
            <router-link
              to="/register"
              class="text-xs font-bold text-white bg-[#262626] hover:bg-[#171717] px-3.5 py-1.5 rounded-[4px] shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] active:scale-[0.98] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626] transition-colors duration-150 ease-out"
            >
              Daftar Gratis
            </router-link>
          </div>
        </template>

        <!-- Kondisi 4: Super Administrator (Role: ADMIN) -->
        <template v-else-if="isSuperAdmin">
          <div class="hidden md:flex items-center space-x-2">
            <!-- Backend Status indicator (clean & compact) -->
            <div class="hidden xl:flex items-center space-x-1.5 px-2 py-1 bg-[#fafafa] border border-[#ededed] rounded-[4px] text-[11px] text-[#065f46]">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span class="font-bold tracking-tight">200 OK</span>
            </div>

            <!-- Unified Admin User Chip -->
            <div class="flex items-center space-x-2 text-xs font-semibold text-[#262626] pl-1.5 pr-2 py-1 rounded-[4px] border border-[#ededed] bg-[#fafafa]">
              <div class="w-5 h-5 rounded-[3px] bg-[#262626] text-white flex items-center justify-center text-[10px] font-extrabold flex-shrink-0">
                {{ userInitial }}
              </div>
              <span class="truncate max-w-[110px] font-bold text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
              <span class="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded-[3px] bg-[#262626] text-white tracking-wider">
                Admin
              </span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="text-xs font-bold text-[#686868] hover:text-[#262626] px-2.5 py-1 rounded-[4px] border border-[#ededed] hover:border-[#d4d4d4] hover:bg-[#fafafa] active:scale-[0.98] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626] transition-colors duration-150 ease-out whitespace-nowrap"
            >
              Keluar
            </button>
          </div>
        </template>

        <!-- Kondisi 3: Dosen / Reviewer (Role: REVIEWER) -->
        <template v-else-if="isReviewer">
          <div class="hidden md:flex items-center space-x-2">
            <div class="flex items-center space-x-2 text-xs font-semibold text-[#262626] pl-1.5 pr-2 py-1 rounded-[4px] border border-[#ededed] bg-[#fafafa]">
              <div class="w-5 h-5 rounded-[3px] bg-[#262626] text-white flex items-center justify-center text-[10px] font-extrabold flex-shrink-0">
                {{ userInitial }}
              </div>
              <span class="truncate max-w-[110px] font-bold text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
              <span class="text-[9px] font-extrabold px-1.5 py-0.5 bg-[#ededed] text-[#262626] rounded-[3px] uppercase tracking-wider">
                Dosen
              </span>
            </div>

            <div class="flex items-center space-x-1.5 px-2.5 py-1 bg-[#ecfdf5] border border-[#a7f3d0] text-[#065f46] rounded-[4px] text-xs">
              <span class="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
              <span class="font-medium text-[11px]">Saldo: <strong class="tabular-nums font-extrabold">{{ authStore.tokenBalance }}</strong> Token</span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="text-xs font-bold text-[#686868] hover:text-[#262626] px-2.5 py-1 rounded-[4px] border border-[#ededed] hover:border-[#d4d4d4] hover:bg-[#fafafa] active:scale-[0.98] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626] transition-colors duration-150 ease-out whitespace-nowrap"
            >
              Keluar
            </button>
          </div>
        </template>

        <!-- Kondisi 2: Mahasiswa Terautentikasi (Role: TRIAL / PREMIUM / USER) -->
        <template v-else>
          <div class="hidden md:flex items-center space-x-2">
            <!-- Chip Profil Terpadu: Avatar + Nama + Status Akun + Saldo Token Aktif -->
            <div class="flex items-center space-x-2 text-xs font-semibold text-[#262626] pl-1.5 pr-2 py-1 rounded-[4px] border border-[#ededed] bg-[#fafafa]">
              <div class="w-5 h-5 rounded-[3px] bg-[#262626] text-white flex items-center justify-center text-[10px] font-extrabold flex-shrink-0">
                {{ userInitial }}
              </div>
              <span class="truncate max-w-[120px] font-bold text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
              <span
                v-if="authStore.role === 'PREMIUM'"
                class="px-1.5 py-0.5 rounded-[3px] text-[9px] font-black tracking-wider bg-[#262626] text-white"
              >
                PREMIUM
              </span>
              <span
                v-else
                class="px-1.5 py-0.5 rounded-[3px] text-[9px] font-bold tracking-wider bg-[#ededed] text-[#686868]"
              >
                TRIAL
              </span>
              <span class="text-[#d4d4d4]">|</span>
              <span class="inline-flex items-center text-[11px] font-medium text-[#065f46]">
                <strong class="tabular-nums font-extrabold mr-1">{{ authStore.tokenBalance }}</strong> Token
              </span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="text-xs font-bold text-[#686868] hover:text-[#262626] px-2.5 py-1 rounded-[4px] border border-[#ededed] hover:border-[#d4d4d4] hover:bg-[#fafafa] active:scale-[0.98] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#262626] transition-colors duration-150 ease-out whitespace-nowrap"
            >
              Keluar
            </button>
          </div>
        </template>

        <!-- Mobile Menu Toggle Button -->
        <button
          type="button"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="md:hidden p-2 rounded-[4px] text-[#686868] hover:text-[#262626] hover:bg-[#fafafa] active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] transition-colors duration-150 ease-out"
          aria-label="Toggle navigasi mobile"
        >
          <svg v-if="!isMobileMenuOpen" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Dropdown Navigation Drawer -->
    <div
      v-if="isMobileMenuOpen"
      class="md:hidden border-t border-[#ededed] bg-white px-4 pt-3 pb-5 space-y-3"
    >
      <!-- Conditional Nav Items for Mobile -->
      <nav class="flex flex-col space-y-1 text-sm font-medium tracking-tight">
        <router-link
          v-for="item in navLinks"
          :key="item.to"
          :to="item.to"
          class="px-3 py-2 rounded-[4px] transition-colors duration-150 ease-out active:scale-[0.98]"
          :class="[
            isItemActive(item.to)
              ? 'text-[#262626] font-semibold bg-[#fafafa]'
              : 'text-[#686868] hover:text-[#262626] hover:bg-[#fafafa]',
          ]"
          @click="closeMobileMenu"
        >
          {{ item.name }}
        </router-link>
      </nav>

      <div class="border-t border-[#ededed] pt-3 flex flex-col space-y-2">
        <!-- Kondisi 1: Tamu (Belum Login) -->
        <template v-if="isGuest">
          <router-link
            to="/login"
            class="w-full text-center py-2 text-sm font-medium text-[#262626] bg-[#fafafa] hover:bg-[#ededed] border border-[#ededed] rounded-[4px] active:scale-[0.98] transition-colors duration-150 ease-out"
            @click="closeMobileMenu"
          >
            Masuk
          </router-link>
          <router-link
            to="/register"
            class="w-full text-center py-2 text-sm font-medium text-white bg-[#262626] hover:bg-[#171717] rounded-[4px] shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] active:scale-[0.98] transition-colors duration-150 ease-out"
            @click="closeMobileMenu"
          >
            Daftar Gratis
          </router-link>
        </template>

        <!-- Kondisi 4: Super Admin -->
        <template v-else-if="isSuperAdmin">
          <div class="flex items-center justify-between px-3 py-2 bg-[#fafafa] border border-[#ededed] rounded-[4px]">
            <div class="flex items-center space-x-2.5 truncate">
              <div class="w-6 h-6 rounded-full bg-[#262626] text-white flex items-center justify-center text-[11px] font-extrabold flex-shrink-0">
                {{ userInitial }}
              </div>
              <div class="flex flex-col text-xs leading-tight truncate">
                <span class="font-bold text-[#262626] truncate">{{ userDisplayName }}</span>
                <span class="text-[10px] text-[#737373] truncate font-medium">{{ authStore.user?.email || 'admin@veritext.ai' }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-1.5 flex-shrink-0">
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] italic font-bold bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
                200 OK
              </span>
              <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-[#262626] text-white uppercase">
                Admin
              </span>
            </div>
          </div>

          <button
            type="button"
            @click="handleLogout"
            class="w-full text-center py-2 text-xs font-bold text-[#262626] bg-[#fafafa] hover:bg-[#ededed] border border-[#ededed] rounded-[4px] active:scale-[0.98] transition-colors duration-150 ease-out"
          >
            Keluar Akun
          </button>
        </template>

        <!-- Kondisi 3: Dosen / Reviewer -->
        <template v-else-if="isReviewer">
          <div class="flex items-center space-x-2.5 px-3 py-2 bg-[#fafafa] border border-[#ededed] rounded-[4px]">
            <div class="w-6 h-6 rounded-full bg-[#262626] text-white flex items-center justify-center text-[11px] font-extrabold flex-shrink-0">
              {{ userInitial }}
            </div>
            <div class="flex flex-col text-xs leading-tight truncate">
              <span class="font-bold text-[#262626] truncate">{{ userDisplayName }}</span>
              <span class="text-[10px] text-[#737373] truncate font-medium">{{ authStore.user?.institution || 'Dosen / Reviewer Terverifikasi' }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between px-3 py-1.5 bg-[#ecfdf5] border border-[#a7f3d0] rounded-[4px] text-xs text-[#065f46] font-medium">
            <span>Saldo Kuota: <strong class="tabular-nums font-extrabold">{{ authStore.tokenBalance }}</strong> Token</span>
            <span class="text-[10px] uppercase italic font-bold px-2 py-0.5 bg-[#ededed] text-[#262626] rounded-full">Reviewer</span>
          </div>

          <button
            type="button"
            @click="handleLogout"
            class="w-full text-center py-2 text-xs font-bold text-[#262626] bg-[#fafafa] hover:bg-[#ededed] border border-[#ededed] rounded-[4px] active:scale-[0.98] transition-colors duration-150 ease-out"
          >
            Keluar Akun
          </button>
        </template>

        <!-- Kondisi 2: Mahasiswa (TRIAL / PREMIUM / USER) -->
        <template v-else>
          <div class="flex items-center space-x-2.5 px-3 py-2 bg-[#fafafa] border border-[#ededed] rounded-[4px]">
            <div class="w-6 h-6 rounded-full bg-[#262626] text-white flex items-center justify-center text-[11px] font-extrabold flex-shrink-0">
              {{ userInitial }}
            </div>
            <div class="flex flex-col text-xs leading-tight truncate">
              <span class="font-bold text-[#262626] truncate">{{ userDisplayName }}</span>
              <span class="text-[10px] text-[#737373] truncate font-medium">{{ authStore.user?.institution || authStore.user?.email || 'Mahasiswa' }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between px-3 py-1.5 bg-[#ecfdf5] border border-[#a7f3d0] rounded-[4px] text-xs text-[#065f46] font-medium">
            <span>Saldo Kuota: <strong class="tabular-nums font-extrabold">{{ authStore.tokenBalance }}</strong> Token</span>
            <span class="text-[10px] uppercase font-bold px-2 py-0.5 bg-[#ededed] text-[#262626] rounded-full">{{ authStore.role }}</span>
          </div>

          <button
            type="button"
            @click="handleLogout"
            class="w-full text-center py-2 text-xs font-bold text-[#262626] bg-[#fafafa] hover:bg-[#ededed] border border-[#ededed] rounded-[4px] active:scale-[0.98] transition-colors duration-150 ease-out"
          >
            Keluar Akun
          </button>
        </template>
      </div>
    </div>
  </header>
</template>
