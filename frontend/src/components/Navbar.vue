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
  <!-- Floating Dark Navbar (Symbol Dark Theme Reference) -->
  <header class="sticky top-0 z-50 py-2 sm:py-3 px-3 sm:px-6 lg:px-8 bg-transparent pointer-events-none select-none">
    <div class="max-w-7xl mx-auto pointer-events-auto">
      <div class="bg-[#12151c]/95 backdrop-blur-md rounded-[20px] border border-white/10 px-4 sm:px-6 h-16 flex items-center justify-between shadow-[0_12px_36px_-10px_rgba(0,0,0,0.6)] transition-all duration-200">
        
        <!-- Left: Brand Logo & Symbol Badge -->
        <router-link
          :to="isSuperAdmin ? '/admin' : '/'"
          class="flex items-center space-x-2.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] rounded-full group"
          @click="closeMobileMenu"
        >
          <!-- Cobalt Blue Round Icon with White Glyph -->
          <div class="w-8 h-8 rounded-full bg-[#2563EB] group-hover:bg-[#1d4ed8] text-white flex items-center justify-center font-bold text-xs shadow-md border border-white/20 transition-colors">
            V
          </div>
          <div class="flex items-center">
            <span class="text-sm sm:text-base font-semibold tracking-tight text-white">
              VeriText<span class="italic font-normal text-[#9ba1b0] ml-0.5">AI</span>
            </span>
            <span
              v-if="isSuperAdmin"
              class="hidden sm:inline-block ml-2 text-[10px] font-mono font-medium uppercase px-2 py-0.5 rounded-full bg-white/10 text-white/80 border border-white/10 tracking-wider"
            >
              Admin
            </span>
            <span
              v-else
              class="hidden sm:inline-block ml-2 text-[10px] font-mono font-medium uppercase px-2 py-0.5 rounded-full bg-white/10 text-[#9ba1b0] border border-white/10 tracking-wider"
            >
              Hybrid
            </span>
          </div>
        </router-link>

        <!-- Center: Desktop Navigation Links (Dark Pill Menu) -->
        <nav class="hidden md:flex items-center space-x-1 text-xs tracking-tight">
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="whitespace-nowrap px-3.5 py-1.5 rounded-full font-medium transition-all duration-150 ease-out focus:outline-none focus-visible:ring-1 focus-visible:ring-white/50"
            :class="[
              isItemActive(item.to)
                ? 'bg-white/15 text-white font-semibold border border-white/15 shadow-sm'
                : 'text-[#9ba1b0] hover:text-white hover:bg-white/5',
            ]"
          >
            {{ item.name }}
          </router-link>
        </nav>

        <!-- Right: Actions, Search Pill & Profile Chip -->
        <div class="flex items-center space-x-2.5 flex-shrink-0">
          <!-- Kondisi 1: Tamu (Belum Login / !authStore.isAuthenticated) -->
          <template v-if="isGuest">
            <div class="hidden md:flex items-center space-x-2.5">
              <!-- Quick Verify Search Pill -->
              <router-link
                to="/verify/sample"
                class="hidden lg:flex items-center space-x-2 bg-[#1c212d] hover:bg-[#252b3a] border border-white/10 px-3.5 py-1.5 rounded-full text-xs text-[#9ba1b0] hover:text-white transition-colors"
              >
                <svg class="w-3.5 h-3.5 text-[#9ba1b0]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Cari Sertifikat...</span>
              </router-link>

              <router-link
                to="/login"
                class="text-xs font-medium text-[#9ba1b0] hover:text-white px-3 py-1.5 transition-colors duration-150 ease-out"
              >
                Masuk
              </router-link>

              <!-- Blue Primary CTA Pill (Symbol Reference) -->
              <router-link
                to="/register"
                class="text-xs font-medium text-white bg-[#2563EB] hover:bg-[#1d4ed8] px-4 py-2 rounded-full active:scale-[0.98] shadow-md transition-all duration-150 ease-out"
              >
                Daftar Gratis
              </router-link>
            </div>
          </template>

          <!-- Kondisi 4: Super Administrator (Role: ADMIN) -->
          <template v-else-if="isSuperAdmin">
            <div class="hidden md:flex items-center space-x-2.5">
              <!-- 200 OK Green Pill -->
              <div class="hidden xl:flex items-center px-2.5 py-1 bg-emerald-950/60 border border-emerald-500/30 rounded-full text-[10px] text-emerald-400 font-mono">
                <span class="font-bold">200 OK</span>
              </div>

              <!-- Admin User Chip -->
              <div class="flex items-center space-x-2 text-xs font-semibold text-white pl-2 pr-2.5 py-1 rounded-full border border-white/10 bg-[#1c212d]">
                <div class="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                  {{ userInitial }}
                </div>
                <span class="truncate max-w-[110px] text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
                <span class="text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded-full bg-white/20 text-white tracking-wider">
                  Admin
                </span>
              </div>

              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#9ba1b0] hover:text-white px-3 py-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Kondisi 3: Dosen / Reviewer (Role: REVIEWER) -->
          <template v-else-if="isReviewer">
            <div class="hidden md:flex items-center space-x-2.5">
              <!-- Token Balance Pill -->
              <div class="flex items-center px-3 py-1 bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 rounded-full text-xs">
                <span class="text-[11px] font-mono">Saldo: <strong class="tabular-nums font-bold">{{ authStore.tokenBalance }}</strong> Token</span>
              </div>

              <!-- Reviewer User Chip -->
              <div class="flex items-center space-x-2 text-xs font-semibold text-white pl-2 pr-2.5 py-1 rounded-full border border-white/10 bg-[#1c212d]">
                <div class="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                  {{ userInitial }}
                </div>
                <span class="truncate max-w-[110px] text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
                <span class="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded-full bg-white/20 text-white tracking-wider">
                  Dosen
                </span>
              </div>

              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#9ba1b0] hover:text-white px-3 py-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Kondisi 2: Mahasiswa Terautentikasi (Role: TRIAL / PREMIUM / USER) -->
          <template v-else>
            <div class="hidden md:flex items-center space-x-2.5">
              <!-- Token Balance Pill -->
              <div class="flex items-center px-3 py-1 bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 rounded-full text-xs">
                <span class="text-[11px] font-mono"><strong class="tabular-nums font-bold">{{ authStore.tokenBalance }}</strong> Token</span>
              </div>

              <!-- Student Profile Chip -->
              <div class="flex items-center space-x-2 text-xs font-semibold text-white pl-2 pr-2.5 py-1 rounded-full border border-white/10 bg-[#1c212d]">
                <div class="w-5 h-5 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                  {{ userInitial }}
                </div>
                <span class="truncate max-w-[120px] text-xs" :title="userDisplayName">{{ userDisplayName }}</span>
                <span
                  v-if="authStore.role === 'PREMIUM'"
                  class="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-[#2563EB] text-white"
                >
                  PREMIUM
                </span>
                <span
                  v-else
                  class="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-white/15 text-[#9ba1b0]"
                >
                  TRIAL
                </span>
              </div>

              <button
                type="button"
                @click="handleLogout"
                class="text-xs font-medium text-[#9ba1b0] hover:text-white px-3 py-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 transition-colors"
              >
                Keluar
              </button>
            </div>
          </template>

          <!-- Mobile Hamburger Toggle -->
          <button
            type="button"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="md:hidden p-2 rounded-full text-[#9ba1b0] hover:text-white hover:bg-white/10 transition-colors"
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

      <!-- Mobile Dark Drawer -->
      <div
        v-if="isMobileMenuOpen"
        class="md:hidden mt-2 bg-[#12151c]/98 backdrop-blur-lg border border-white/10 rounded-[20px] p-4 text-white shadow-2xl space-y-3"
      >
        <!-- Nav Links -->
        <nav class="flex flex-col space-y-1 text-sm font-medium tracking-tight">
          <router-link
            v-for="item in navLinks"
            :key="item.to"
            :to="item.to"
            class="px-3 py-2 rounded-full transition-colors"
            :class="[
              isItemActive(item.to)
                ? 'text-white font-semibold bg-white/15'
                : 'text-[#9ba1b0] hover:text-white hover:bg-white/5',
            ]"
            @click="closeMobileMenu"
          >
            {{ item.name }}
          </router-link>
        </nav>

        <div class="border-t border-white/10 pt-3 flex flex-col space-y-2">
          <!-- Kondisi 1: Tamu (Belum Login) -->
          <template v-if="isGuest">
            <router-link
              to="/login"
              class="w-full text-center py-2.5 text-xs font-medium text-[#9ba1b0] hover:text-white bg-white/5 border border-white/10 rounded-full transition-colors"
              @click="closeMobileMenu"
            >
              Masuk
            </router-link>
            <router-link
              to="/register"
              class="w-full text-center py-2.5 text-xs font-medium text-white bg-[#2563EB] hover:bg-[#1d4ed8] rounded-full shadow-md transition-colors"
              @click="closeMobileMenu"
            >
              Daftar Gratis
            </router-link>
          </template>

          <!-- Kondisi 4: Super Admin -->
          <template v-else-if="isSuperAdmin">
            <div class="flex items-center justify-between px-3 py-2 bg-white/5 border border-white/10 rounded-[14px]">
              <div class="flex items-center space-x-2.5 truncate">
                <div class="w-6 h-6 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                  {{ userInitial }}
                </div>
                <div class="flex flex-col text-xs leading-tight truncate">
                  <span class="font-bold text-white truncate">{{ userDisplayName }}</span>
                  <span class="text-[10px] text-[#9ba1b0] truncate">{{ authStore.user?.email || 'admin@veritext.ai' }}</span>
                </div>
              </div>
              <div class="flex items-center space-x-1.5 flex-shrink-0">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[9px] bg-emerald-950 border border-emerald-500/30 text-emerald-400 font-mono">
                  200 OK
                </span>
                <span class="px-2 py-0.5 text-[10px] font-mono font-bold rounded-full bg-white/20 text-white uppercase">
                  Admin
                </span>
              </div>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="w-full text-center py-2 text-xs font-medium text-[#9ba1b0] hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-colors"
            >
              Keluar Akun
            </button>
          </template>

          <!-- Kondisi 3: Dosen / Reviewer -->
          <template v-else-if="isReviewer">
            <div class="flex items-center space-x-2.5 px-3 py-2 bg-white/5 border border-white/10 rounded-[14px]">
              <div class="w-6 h-6 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                {{ userInitial }}
              </div>
              <div class="flex flex-col text-xs leading-tight truncate">
                <span class="font-bold text-white truncate">{{ userDisplayName }}</span>
                <span class="text-[10px] text-[#9ba1b0] truncate">{{ authStore.user?.institution || 'Dosen / Reviewer' }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between px-3 py-1.5 bg-emerald-950/60 border border-emerald-500/30 rounded-full text-xs text-emerald-400">
              <span class="font-mono">Saldo: <strong class="tabular-nums font-bold">{{ authStore.tokenBalance }}</strong> Token</span>
              <span class="text-[10px] uppercase font-mono px-2 py-0.5 bg-white/20 text-white rounded-full">Reviewer</span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="w-full text-center py-2 text-xs font-medium text-[#9ba1b0] hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-colors"
            >
              Keluar Akun
            </button>
          </template>

          <!-- Kondisi 2: Mahasiswa (TRIAL / PREMIUM / USER) -->
          <template v-else>
            <div class="flex items-center space-x-2.5 px-3 py-2 bg-white/5 border border-white/10 rounded-[14px]">
              <div class="w-6 h-6 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                {{ userInitial }}
              </div>
              <div class="flex flex-col text-xs leading-tight truncate">
                <span class="font-bold text-white truncate">{{ userDisplayName }}</span>
                <span class="text-[10px] text-[#9ba1b0] truncate">{{ authStore.user?.institution || authStore.user?.email || 'Mahasiswa' }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between px-3 py-1.5 bg-emerald-950/60 border border-emerald-500/30 rounded-full text-xs text-emerald-400">
              <span class="font-mono">Saldo: <strong class="tabular-nums font-bold">{{ authStore.tokenBalance }}</strong> Token</span>
              <span class="text-[10px] uppercase font-mono px-2 py-0.5 bg-white/20 text-white rounded-full">{{ authStore.role }}</span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              class="w-full text-center py-2 text-xs font-medium text-[#9ba1b0] hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-colors"
            >
              Keluar Akun
            </button>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
