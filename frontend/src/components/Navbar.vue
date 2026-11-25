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
const userEmail = computed(() => authStore.user?.email || "");
const balance = computed(() => Number(authStore.tokenBalance) || 0);

function isItemActive(to: string): boolean {
  if (to.includes("#")) {
    const [p, h] = to.split("#");
    return route.path === p && route.hash === `#${h}`;
  }
  if (to === "/" || to === "/admin") return route.path === to;
  return route.path.startsWith(to);
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

  <header class="pointer-events-none fixed inset-x-0 top-0 z-50 select-none px-3 transition-all duration-300 sm:px-5" :class="isScrolled ? 'pt-3' : 'pt-0'">
    <div
      class="pointer-events-auto relative mx-auto w-full transition-all duration-300"
      :class="isScrolled
        ? 'max-w-[1120px] rounded-full border border-white/60 bg-white/70 px-5 shadow-[0_12px_32px_-10px_rgba(20,17,28,0.12)] backdrop-blur-md sm:px-6'
        : 'max-w-[1180px] bg-transparent px-1 sm:px-2'"
    >
      <div class="flex items-center justify-between transition-[height] duration-300" :class="isScrolled ? 'h-[56px]' : 'h-[64px]'">
        <div class="flex items-center gap-6 lg:gap-8">
          <router-link
            :to="isGuest ? '/' : isAdmin ? '/admin' : '/dashboard'"
            class="inline-flex h-10 flex-shrink-0 items-center rounded-full text-[19px] font-semibold tracking-[-0.03em] text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            @click="closeMenu"
          >
            VeriText <span class="ml-1 text-[#0F766E]">AI</span>
          </router-link>

          <div class="hidden lg:flex items-center">
            <NavLinks :links="navLinks" :is-active="isItemActive" />
          </div>
        </div>

        <div class="flex items-center justify-end gap-2">
          <NavAuthActions class="hidden lg:flex" :is-guest="isGuest" :is-admin="isAdmin" :name="displayName" :email="userEmail" :role="authStore.role" :balance="balance" :menu-links="menuLinks" @logout="handleLogout" />

          <div class="flex items-center gap-2 lg:hidden">
            <router-link
              v-if="isGuest"
              to="/register"
              class="vt-btn-dark inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-[13px] font-semibold"
              @click="closeMenu"
            >Daftar</router-link>
            <button
              type="button"
              class="relative flex h-10 w-10 cursor-pointer items-center justify-center rounded-full transition-colors duration-200 hover:bg-[#14111C]/[0.05] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
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
