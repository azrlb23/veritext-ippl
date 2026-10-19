<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { getSegmentedNavLinks } from "../utils/navigation";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();

// State for Mobile Drawer & Scroll-based Auto Collapse
const isMobileMenuOpen = ref(false);
const isScrolled = ref(false);

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

// Otomatis Collapse Berdasarkan Scrolling:
// Di atas halaman (scrollY <= 40): Besar / Spacious
// Scroll ke bawah (scrollY > 40): Otomatis Collapse menjadi Kapsul Ramping
function handleScroll() {
  isScrolled.value = window.scrollY > 40;
}

onMounted(() => {
  handleScroll();
  window.addEventListener("scroll", handleScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

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
  <!-- Floating Capsule Container (Centering wrapper) -->
  <header
    class="fixed left-0 right-0 z-50 flex justify-center px-3 sm:px-4 pointer-events-none select-none transition-all duration-300 ease-out"
    :class="isScrolled ? 'top-2.5 sm:top-3' : 'top-4 sm:top-6'"
  >
    <div
      class="pointer-events-auto transition-all duration-300 ease-out"
      :class="[
        // Base Glass Island Styling
        'border border-[#ededed]',
        // SCROLL-COLLAPSED (Kapsul Ramping saat scroll ke bawah)
        isScrolled
          ? 'bg-white/85 backdrop-blur-lg shadow-[0_10px_30px_-5px_rgba(4,23,43,0.1),0_1px_3px_rgba(0,0,0,0.05)] rounded-full px-3.5 sm:px-5 py-1.5 w-auto max-w-fit flex items-center justify-between gap-3 sm:gap-6'
          // AT TOP (Besar & Lega saat di paling atas)
          : isMobileMenuOpen
            ? 'bg-white/95 backdrop-blur-md shadow-[0_4px_24px_-4px_rgba(4,23,43,0.06)] rounded-[24px] sm:rounded-full w-full max-w-5xl px-4 sm:px-7 py-3'
            : 'bg-white/95 backdrop-blur-md shadow-[0_4px_24px_-4px_rgba(4,23,43,0.06)] rounded-full w-full max-w-5xl px-4 sm:px-7 py-3 flex items-center justify-between'
      ]"
    >
      <!-- Top Row inside Capsule -->
      <div class="flex items-center justify-between w-full gap-3 sm:gap-6">
        <!-- 1. Brand Logo (Left) -->
        <router-link
          :to="isSuperAdmin ? '/admin' : '/'"
          class="flex items-center space-x-2 focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c] rounded-full flex-shrink-0"
          @click="closeMobileMenu"
        >
          <!-- Logo Circle Icon -->
          <div
            class="rounded-full bg-[#17191c] flex items-center justify-center text-white font-semibold shadow-sm transition-all duration-300"
            :class="isScrolled ? 'w-6 h-6 text-[10px]' : 'w-7 h-7 text-xs'"
          >
            V
          </div>
          <!-- Logo Text -->
          <div class="flex items-center">
            <span
              class="font-semibold tracking-tight text-[#17191c] transition-all duration-300"
              :class="isScrolled ? 'text-xs' : 'text-sm'"
            >
              VeriText<span class="italic font-normal text-[#777b86] ml-0.5">AI</span>
            </span>
            <!-- Tag hanya muncul saat di atas (belum scroll) -->
            <span
              v-if="!isScrolled && isSuperAdmin"
              class="hidden lg:inline-block ml-2 text-[9px] font-medium uppercase px-2 py-0.5 rounded-full bg-[#f2f2f3] text-[#17191c] tracking-wider transition-opacity duration-300"
            >
              Admin
            </span>
            <span
              v-else-if="!isScrolled"
              class="hidden lg:inline-block ml-2 text-[9px] font-medium uppercase px-2 py-0.5 rounded-full bg-[#f2f2f3] text-[#777b86] tracking-wider transition-opacity duration-300"
            >
              Hybrid
            </span>
          </div>
        </router-link>

        <!-- 2. Segmented Navigation Links (Center - Desktop) -->
        <nav
          class="hidden md:flex items-center text-xs tracking-tight transition-all duration-300"
          :class="isScrolled ? 'space-x-0.5' : 'space-x-1.5'"
        >
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="whitespace-nowrap rounded-full font-medium transition-all duration-200 ease-out focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c]"
            :class="[
              isScrolled ? 'px-3 py-1 text-[11px]' : 'px-3.5 py-1.5 text-xs',
              isItemActive(item.to)
                ? 'bg-[#17191c] text-white shadow-sm'
                : 'text-[#777b86] hover:text-[#17191c] hover:bg-[#f2f2f3]/80',
            ]"
          >
            {{ item.name }}
          </router-link>
        </nav>

        <!-- 3. Actions / User Profile (Right) -->
        <div class="flex items-center space-x-2 flex-shrink-0">
          <!-- Kondisi 1: Tamu (Belum Login) -->
          <template v-if="isGuest">
            <div class="hidden md:flex items-center space-x-2">
              <router-link
                to="/login"
                class="font-medium text-[#777b86] hover:text-[#17191c] transition-colors"
                :class="isScrolled ? 'text-xs px-2.5 py-1' : 'text-xs px-3.5 py-1.5'"
              >
                Masuk
              </router-link>
              <router-link
                to="/register"
                class="font-medium text-white bg-[#17191c] hover:bg-[#2b2e34] rounded-full active:scale-[0.98] transition-all shadow-sm"
                :class="isScrolled ? 'text-xs px-3 py-1' : 'text-xs px-4 py-1.5'"
              >
                Daftar
              </router-link>
            </div>
          </template>

          <!-- Kondisi 4: Super Administrator (Role: ADMIN) -->
          <template v-else-if="isSuperAdmin">
            <div class="hidden md:flex items-center space-x-2 text-xs">
              <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                <div class="w-4 h-4 rounded-full bg-[#17191c] text-white flex items-center justify-center text-[9px] font-bold">
                  {{ userInitial }}
                </div>
                <span class="truncate max-w-[90px]">{{ userDisplayName }}</span>
              </div>
              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Kondisi 3: Dosen / Reviewer (Role: REVIEWER) -->
          <template v-else-if="isReviewer">
            <div class="hidden md:flex items-center space-x-2 text-xs">
              <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                <span class="truncate max-w-[90px]">{{ userDisplayName }}</span>
                <span class="text-[10px] text-[#059669] font-bold tabular-nums">({{ authStore.tokenBalance }} T)</span>
              </div>
              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Kondisi 2: Mahasiswa (TRIAL / PREMIUM / USER) -->
          <template v-else>
            <div class="hidden md:flex items-center space-x-2 text-xs">
              <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                <div class="w-4 h-4 rounded-full bg-[#17191c] text-white flex items-center justify-center text-[9px] font-bold">
                  {{ userInitial }}
                </div>
                <span class="truncate max-w-[90px]">{{ userDisplayName }}</span>
                <span class="text-[10px] text-[#059669] font-bold tabular-nums">{{ authStore.tokenBalance }} T</span>
              </div>
              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Mobile Menu Hamburger / Close Toggle Button -->
          <button
            type="button"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="md:hidden p-1.5 rounded-full text-[#777b86] hover:text-[#17191c] hover:bg-[#f2f2f3] focus:outline-none transition-colors"
            aria-label="Toggle menu navigasi"
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

      <!-- Mobile Dropdown Navigation Drawer (Unfolds smoothly inside the capsule on mobile) -->
      <div
        v-if="isMobileMenuOpen"
        class="md:hidden pt-4 pb-2 border-t border-[#ededed] mt-3 space-y-3"
      >
        <!-- Nav Links for Mobile -->
        <nav class="flex flex-col space-y-1 text-xs font-medium">
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="px-3.5 py-2 rounded-full transition-colors"
            :class="[
              isItemActive(item.to)
                ? 'bg-[#17191c] text-white font-medium'
                : 'text-[#777b86] hover:text-[#17191c] hover:bg-[#f2f2f3]',
            ]"
            @click="closeMobileMenu"
          >
            {{ item.name }}
          </router-link>
        </nav>

        <!-- Auth Actions for Mobile -->
        <div class="pt-2 border-t border-[#ededed] flex items-center justify-between">
          <template v-if="isGuest">
            <router-link
              to="/login"
              class="text-xs font-medium text-[#777b86] px-3 py-1.5"
              @click="closeMobileMenu"
            >
              Masuk
            </router-link>
            <router-link
              to="/register"
              class="text-xs font-medium text-white bg-[#17191c] px-4 py-1.5 rounded-full"
              @click="closeMobileMenu"
            >
              Daftar Gratis
            </router-link>
          </template>
          <template v-else>
            <div class="flex items-center space-x-2 text-xs">
              <div class="w-5 h-5 rounded-full bg-[#17191c] text-white flex items-center justify-center font-bold text-[10px]">
                {{ userInitial }}
              </div>
              <span class="font-medium text-[#17191c]">{{ userDisplayName }}</span>
            </div>
            <button
              type="button"
              @click="handleLogout"
              class="text-xs text-[#b91c1c] font-medium px-2 py-1"
            >
              Keluar
            </button>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
