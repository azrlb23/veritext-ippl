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

// State for Mobile Drawer & Capsule Collapse
const isMobileMenuOpen = ref(false);
const isCollapsed = ref(false);
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

// Active Route Name for Collapsed Micro-Pill
const activeRouteName = computed(() => {
  const active = navLinks.value.find((item) => isItemActive(item.to));
  if (active) return active.name;
  if (route.path.startsWith("/audits/")) return "Laporan Audit";
  return "Menu";
});

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

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value;
  if (isCollapsed.value) {
    isMobileMenuOpen.value = false;
  }
}

// Auto scroll tracking for smart collapse
function handleScroll() {
  isScrolled.value = window.scrollY > 80;
}

onMounted(() => {
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
  <!-- Floating Capsule Container (Centered at top with gentle clearance) -->
  <header class="fixed top-3 sm:top-4 left-0 right-0 z-50 flex justify-center px-3 sm:px-4 pointer-events-none select-none">
    <div
      class="pointer-events-auto transition-all duration-300 ease-out"
      :class="[
        // Base Glass Island Styling
        'bg-white/90 backdrop-blur-md border border-[#ededed] shadow-[0_6px_24px_-4px_rgba(4,23,43,0.08),0_1px_2px_rgba(0,0,0,0.04)]',
        // Desktop Collapsed vs Expanded Shapes
        isCollapsed
          ? 'rounded-full px-3 py-1.5 flex items-center space-x-2.5 max-w-fit'
          : isMobileMenuOpen
            ? 'rounded-[24px] sm:rounded-full w-full max-w-4xl px-3.5 sm:px-5 py-2'
            : 'rounded-full w-full max-w-4xl px-3.5 sm:px-5 py-2 flex items-center justify-between',
        // Hover state when collapsed
        isCollapsed ? 'hover:bg-white hover:shadow-md cursor-pointer' : ''
      ]"
    >
      <!-- ============================================================ -->
      <!-- STATE A: COLLAPSED MICRO-CAPSULE (Compact Island Pill)      -->
      <!-- ============================================================ -->
      <template v-if="isCollapsed">
        <!-- Logo Icon -->
        <router-link
          :to="isSuperAdmin ? '/admin' : '/'"
          class="flex items-center space-x-2 focus:outline-none"
          title="VeriText AI"
        >
          <div class="w-6 h-6 rounded-full bg-[#17191c] flex items-center justify-center text-white font-semibold text-xs shadow-sm">
            V
          </div>
          <span class="text-xs font-semibold text-[#17191c] tracking-tight hidden sm:inline-block">
            VeriText
          </span>
        </router-link>

        <span class="text-[#ededed]">&bull;</span>

        <!-- Active Page Chip -->
        <span class="text-[11px] font-medium text-[#17191c] px-2.5 py-0.5 rounded-full bg-[#f2f2f3]">
          {{ activeRouteName }}
        </span>

        <!-- Expand Button (+) -->
        <button
          type="button"
          @click.stop="toggleCollapse"
          class="w-6 h-6 rounded-full bg-[#17191c] hover:bg-[#2e3138] text-white flex items-center justify-center transition-transform active:scale-95"
          title="Buka Navigasi Penuh (Expand Navbar)"
          aria-label="Expand Navbar"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </template>

      <!-- ============================================================ -->
      <!-- STATE B: EXPANDED FULL CAPSULE NAVBAR                       -->
      <!-- ============================================================ -->
      <template v-else>
        <!-- Top Bar Row inside Capsule -->
        <div class="flex items-center justify-between w-full">
          <!-- 1. Brand Logo (Left) -->
          <router-link
            :to="isSuperAdmin ? '/admin' : '/'"
            class="flex items-center space-x-2.5 focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c] rounded-full flex-shrink-0"
            @click="closeMobileMenu"
          >
            <div class="w-7 h-7 rounded-full bg-[#17191c] flex items-center justify-center text-white font-semibold text-xs shadow-sm">
              V
            </div>
            <div class="flex items-center">
              <span class="text-sm font-semibold tracking-tight text-[#17191c]">
                VeriText<span class="italic font-normal text-[#777b86] ml-0.5">AI</span>
              </span>
              <span
                v-if="isSuperAdmin"
                class="hidden lg:inline-block ml-1.5 text-[9px] font-medium uppercase px-2 py-0.5 rounded-full bg-[#f2f2f3] text-[#17191c] tracking-wider"
              >
                Admin
              </span>
            </div>
          </router-link>

          <!-- 2. Segmented Pill Links (Center - Desktop) -->
          <nav class="hidden md:flex items-center space-x-1 text-xs tracking-tight">
            <router-link
              v-for="item in navLinks"
              :key="item.to"
              :to="item.to"
              class="whitespace-nowrap px-3.5 py-1.5 rounded-full font-medium transition-all duration-150 ease-out focus:outline-none focus-visible:ring-1 focus-visible:ring-[#17191c]"
              :class="[
                isItemActive(item.to)
                  ? 'bg-[#17191c] text-white font-medium shadow-sm'
                  : 'text-[#777b86] hover:text-[#17191c] hover:bg-[#f2f2f3]/80',
              ]"
            >
              {{ item.name }}
            </router-link>
          </nav>

          <!-- 3. Actions & Collapse Controls (Right) -->
          <div class="flex items-center space-x-2 flex-shrink-0">
            <!-- Condition 1: Tamu (Belum Login) -->
            <template v-if="isGuest">
              <div class="hidden md:flex items-center space-x-2">
                <router-link
                  to="/login"
                  class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-3 py-1.5 transition-colors"
                >
                  Masuk
                </router-link>
                <router-link
                  to="/register"
                  class="text-xs font-medium text-white bg-[#17191c] hover:bg-[#2b2e34] px-4 py-1.5 rounded-full active:scale-[0.98] transition-all shadow-sm"
                >
                  Daftar
                </router-link>
              </div>
            </template>

            <!-- Condition 4: Super Administrator (ADMIN) -->
            <template v-else-if="isSuperAdmin">
              <div class="hidden md:flex items-center space-x-2 text-xs">
                <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                  <div class="w-4 h-4 rounded-full bg-[#17191c] text-white flex items-center justify-center text-[9px] font-bold">
                    {{ userInitial }}
                  </div>
                  <span class="truncate max-w-[100px]">{{ userDisplayName }}</span>
                </div>
                <button
                  type="button"
                  @click="handleLogout"
                  class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2.5 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
                >
                  Keluar
                </button>
              </div>
            </template>

            <!-- Condition 3: Dosen / Reviewer (REVIEWER) -->
            <template v-else-if="isReviewer">
              <div class="hidden md:flex items-center space-x-2 text-xs">
                <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                  <span class="truncate max-w-[100px]">{{ userDisplayName }}</span>
                  <span class="text-[10px] text-[#059669] font-bold tabular-nums">({{ authStore.tokenBalance }} T)</span>
                </div>
                <button
                  type="button"
                  @click="handleLogout"
                  class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2.5 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
                >
                  Keluar
                </button>
              </div>
            </template>

            <!-- Condition 2: Mahasiswa (TRIAL / PREMIUM / USER) -->
            <template v-else>
              <div class="hidden md:flex items-center space-x-2 text-xs">
                <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#f2f2f3] border border-[#ededed] text-[#17191c] font-medium">
                  <div class="w-4 h-4 rounded-full bg-[#17191c] text-white flex items-center justify-center text-[9px] font-bold">
                    {{ userInitial }}
                  </div>
                  <span class="truncate max-w-[100px]">{{ userDisplayName }}</span>
                  <span class="text-[10px] text-[#059669] font-bold tabular-nums">{{ authStore.tokenBalance }} T</span>
                </div>
                <button
                  type="button"
                  @click="handleLogout"
                  class="text-xs font-medium text-[#777b86] hover:text-[#17191c] px-2.5 py-1 rounded-full hover:bg-[#f2f2f3] transition-colors"
                >
                  Keluar
                </button>
              </div>
            </template>

            <!-- Desktop Collapse Button (-) -->
            <button
              type="button"
              @click="toggleCollapse"
              class="hidden md:flex w-7 h-7 rounded-full bg-[#f2f2f3] hover:bg-[#ededed] text-[#777b86] hover:text-[#17191c] items-center justify-center transition-colors"
              title="Kecilkan Navbar (Collapse Capsule)"
              aria-label="Collapse Navbar"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4" />
              </svg>
            </button>

            <!-- Mobile Drawer Toggle (Hamburger / Close) -->
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

        <!-- Mobile Drawer Unfolded Panel (Clean Dropdown Inside the Capsule) -->
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
      </template>
    </div>
  </header>
</template>
