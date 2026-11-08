<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables/useNotification";
import { getAccountMenuLinks, getSegmentedNavLinks } from "../utils/navigation";
import NavAuthActions from "./navbar/NavAuthActions.vue";
import NavLinks from "./navbar/NavLinks.vue";
import NavMobileMenu from "./navbar/NavMobileMenu.vue";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const isMenuOpen = ref(false);
const isScrolled = ref(false);

const isGuest = computed(() => !authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAuthenticated && (authStore.role === "ADMIN" || Boolean(authStore.isAdmin)));
const navLinks = computed(() => getSegmentedNavLinks(authStore.isAuthenticated, authStore.role));
const menuLinks = computed(() => getAccountMenuLinks(authStore.role));
const displayName = computed(() => authStore.user?.full_name || "Pengguna");
const balance = computed(() => Number(authStore.tokenBalance) || 0);

function isItemActive(to: string): boolean {
  if (to.includes("#")) {
    const [p, h] = to.split("#");
    return route.path === p && route.hash === `#${h}`;
  }
  if (to === "/admin") return route.path === "/admin" && (!route.hash || route.hash === "#overview");
  return to === "/" ? route.path === "/" : route.path.startsWith(to);
}

function closeMenu() {
  isMenuOpen.value = false;
}
watch(() => [route.path, route.hash], closeMenu);

async function handleLogout() {
  closeMenu();
  await authStore.logout();
  showNotification("Anda telah berhasil keluar dari akun.", "info", "Sesi Berakhir");
  router.push("/login");
}

const onScroll = () => { isScrolled.value = window.scrollY > 12; };
const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") closeMenu(); };

onMounted(() => {
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  window.removeEventListener("scroll", onScroll);
  window.removeEventListener("keydown", onKey);
});
</script>

<template>
  <div v-if="isMenuOpen" class="fixed inset-0 z-40 bg-[#14111C]/10 backdrop-blur-[2px] lg:hidden" aria-hidden="true" @click="closeMenu"></div>

  <header class="pointer-events-none fixed inset-x-0 top-0 z-50 flex select-none justify-center px-3 pt-3 sm:px-5 sm:pt-4">
    <div class="pointer-events-auto relative w-full max-w-[1120px]">
      <div
        class="grid grid-cols-[auto_1fr] lg:grid-cols-[1fr_auto_1fr] items-center rounded-full bg-white/80 px-4 sm:px-6 backdrop-blur-2xl transition-all duration-300 border border-[#14111C]/[0.04]"
        :class="isScrolled ? 'h-[56px] shadow-float' : 'h-[62px] shadow-lift'"
      >
        <div class="flex items-center justify-start">
          <router-link
            :to="isGuest ? '/' : isAdmin ? '/admin' : '/dashboard'"
            class="inline-flex h-10 flex-shrink-0 items-center rounded-full text-[19px] font-semibold tracking-[-0.03em] text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            @click="closeMenu"
          >
            VeriText <span class="ml-1 text-[#8A3FE0]">AI</span>
          </router-link>
        </div>

        <div class="hidden lg:flex items-center justify-center">
          <NavLinks :links="navLinks" :is-active="isItemActive" />
        </div>

        <div class="flex items-center justify-end gap-2">
          <NavAuthActions class="hidden lg:flex" :is-guest="isGuest" :is-admin="isAdmin" :name="displayName" :balance="balance" :menu-links="menuLinks" @logout="handleLogout" />

          <div class="flex items-center gap-2 lg:hidden">
            <router-link
              v-if="isGuest"
              to="/register"
              class="inline-flex h-9 cursor-pointer items-center rounded-full bg-[#14111C] px-4 text-[13px] font-semibold text-white shadow-btn-dark"
              @click="closeMenu"
            >Daftar</router-link>
            <button
              type="button"
              class="relative flex h-10 w-10 cursor-pointer items-center justify-center rounded-full transition-colors duration-200 hover:bg-[#14111C]/[0.05] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
              :aria-expanded="isMenuOpen"
              aria-controls="menu-navigasi"
              aria-label="Buka menu navigasi"
              @click="isMenuOpen = !isMenuOpen"
            >
              <span class="relative block h-[14px] w-[18px]">
                <span class="absolute left-0 h-[2px] w-full rounded-full bg-[#14111C] transition-all duration-300" :class="isMenuOpen ? 'top-[6px] rotate-45' : 'top-0'"></span>
                <span class="absolute left-0 h-[2px] w-full rounded-full bg-[#14111C] transition-all duration-300" :class="isMenuOpen ? 'top-[6px] -rotate-45' : 'top-[12px]'"></span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="-translate-y-2 opacity-0"
        leave-active-class="transition duration-150 ease-in"
        leave-to-class="-translate-y-2 opacity-0"
      >
        <NavMobileMenu
          v-if="isMenuOpen"
          class="lg:hidden"
          :links="navLinks"
          :extra-links="isGuest ? [] : menuLinks"
          :is-active="isItemActive"
          :is-guest="isGuest"
          :is-admin="isAdmin"
          :name="displayName"
          :balance="balance"
          @close="closeMenu"
          @logout="handleLogout"
        />
      </Transition>
    </div>
  </header>
</template>
