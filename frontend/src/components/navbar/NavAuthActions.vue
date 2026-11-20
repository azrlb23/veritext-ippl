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
    <div v-if="isGuest" class="inline-flex items-center rounded-full border border-[#ECECEF] bg-white p-1 shadow-[0_6px_20px_-6px_rgba(20,17,28,0.12)]">
      <router-link
        to="/login"
        class="inline-flex h-8 cursor-pointer items-center rounded-full px-4 text-[13.5px] font-medium text-[#4B4757] transition-colors duration-200 hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
      >Masuk</router-link>
      <router-link
        to="/register"
        class="inline-flex h-8 cursor-pointer items-center rounded-full bg-gradient-to-b from-[#2A2633] to-[#110E18] px-4 text-[13.5px] font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.22),0_4px_12px_-2px_rgba(17,14,24,0.45)] transition-all duration-200 hover:brightness-110 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
      >Daftar</router-link>
    </div>
    <template v-else>
      <div ref="root" class="relative">
        <button
          type="button"
          class="flex h-10 cursor-pointer items-center gap-2 rounded-full bg-[#14111C]/[0.04] p-1 pr-3 transition-colors hover:bg-[#14111C]/[0.08] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          aria-haspopup="menu"
          :aria-expanded="open"
          @click="open = !open"
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#0F766E] to-[#0D9488] text-[12.5px] font-semibold text-white shadow-sm">
            {{ name.charAt(0).toUpperCase() }}
          </span>
          <span class="max-w-[100px] truncate text-[13px] font-medium text-[#14111C]">{{ name.split(' ')[0] }}</span>
          <svg class="h-3.5 w-3.5 text-[#5E5A6B] transition-transform duration-200" :class="open ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </button>
        <div v-if="open" role="menu" class="absolute right-0 top-full mt-2 w-56 rounded-[22px] bg-white p-2 shadow-float border border-[#14111C]/[0.04]">
          <div class="px-3 py-2 mb-1 rounded-[14px] bg-[#EBF8F6]">
            <div class="text-[13px] font-semibold text-[#14111C] truncate">{{ name }}</div>
            <div v-if="!isAdmin" class="mt-0.5 text-[11.5px] font-semibold text-[#0F766E] tabular-nums">{{ balance }} Token aktif</div>
          </div>
          <router-link
            v-for="l in menuLinks"
            :key="l.to"
            :to="l.to"
            role="menuitem"
            class="flex h-9 cursor-pointer items-center rounded-[12px] px-3 text-[13.5px] font-medium text-[#14111C] transition-colors hover:bg-[#EBF8F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            @click="open = false"
          >{{ l.name }}</router-link>
          <div class="my-1 border-t border-[#14111C]/[0.06]"></div>
          <button
            type="button"
            role="menuitem"
            class="flex h-9 w-full cursor-pointer items-center rounded-[12px] px-3 text-[13.5px] font-medium text-[#EF4444] transition-colors hover:bg-[#FEE2E2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            @click="open = false; $emit('logout')"
          >Keluar</button>
        </div>
      </div>
    </template>
  </div>
</template>
