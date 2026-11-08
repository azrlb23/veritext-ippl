<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

interface LinkItem { name: string; to: string }
defineProps<{ isGuest: boolean; isAdmin: boolean; name: string; balance: number; menuLinks: LinkItem[] }>();
defineEmits<{ (e: "logout"): void }>();

const open = ref(false);
const root = ref<HTMLElement | null>(null);
const onDoc = (e: MouseEvent) => { if (root.value && !root.value.contains(e.target as Node)) open.value = false; };
const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") open.value = false; };
onMounted(() => { document.addEventListener("click", onDoc); document.addEventListener("keydown", onKey); });
onBeforeUnmount(() => { document.removeEventListener("click", onDoc); document.removeEventListener("keydown", onKey); });
</script>

<template>
  <div class="flex items-center gap-2">
    <template v-if="isGuest">
      <router-link
        to="/login"
        class="inline-flex h-10 cursor-pointer items-center rounded-full px-3.5 text-[13.5px] font-medium text-[#4B4757] transition-colors duration-200 hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
      >Masuk</router-link>
      <router-link
        to="/register"
        class="inline-flex h-10 cursor-pointer items-center rounded-full bg-[#14111C] px-5 text-[13.5px] font-semibold text-white shadow-btn-dark transition-all duration-200 hover:-translate-y-0.5 hover:bg-[#2B2438] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
      >Daftar</router-link>
    </template>
    <template v-else>
      <div ref="root" class="relative">
        <button
          type="button"
          class="flex h-10 cursor-pointer items-center gap-2 rounded-full bg-[#14111C]/[0.04] p-1 pr-3 transition-colors hover:bg-[#14111C]/[0.08] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          aria-haspopup="menu"
          :aria-expanded="open"
          @click="open = !open"
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#8A3FE0] to-[#D26BE6] text-[12.5px] font-semibold text-white shadow-sm">
            {{ name.charAt(0).toUpperCase() }}
          </span>
          <span class="max-w-[100px] truncate text-[13px] font-medium text-[#14111C]">{{ name.split(' ')[0] }}</span>
          <svg class="h-3.5 w-3.5 text-[#5E5A6B] transition-transform duration-200" :class="open ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </button>
        <div v-if="open" role="menu" class="absolute right-0 top-full mt-2 w-56 rounded-[22px] bg-white p-2 shadow-float border border-[#14111C]/[0.04]">
          <div class="px-3 py-2 mb-1 rounded-[14px] bg-[#F3EEFA]/70">
            <div class="text-[13px] font-semibold text-[#14111C] truncate">{{ name }}</div>
            <div v-if="!isAdmin" class="mt-0.5 text-[11.5px] font-semibold text-[#6D28D9] tabular-nums">{{ balance }} Token aktif</div>
          </div>
          <router-link
            v-for="l in menuLinks"
            :key="l.to"
            :to="l.to"
            role="menuitem"
            class="flex h-9 cursor-pointer items-center rounded-[12px] px-3 text-[13.5px] font-medium text-[#14111C] transition-colors hover:bg-[#F3EEFA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            @click="open = false"
          >{{ l.name }}</router-link>
          <div class="my-1 border-t border-[#14111C]/[0.06]"></div>
          <button
            type="button"
            role="menuitem"
            class="flex h-9 w-full cursor-pointer items-center rounded-[12px] px-3 text-[13.5px] font-medium text-[#EF4444] transition-colors hover:bg-[#FEE2E2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            @click="open = false; $emit('logout')"
          >Keluar</button>
        </div>
      </div>
    </template>
  </div>
</template>
