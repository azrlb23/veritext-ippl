<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

interface LinkItem { name: string; to: string }
defineProps<{ isGuest: boolean; isAdmin: boolean; name: string; email?: string; role?: string; balance: number; menuLinks: LinkItem[] }>();
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
      <router-link to="/login" class="inline-flex h-8 cursor-pointer items-center rounded-full px-4 text-[13.5px] font-medium text-[#4B4757] transition-colors hover:text-[#14111C]">Masuk</router-link>
      <router-link to="/register" class="inline-flex h-8 cursor-pointer items-center rounded-full bg-gradient-to-b from-[#2A2633] to-[#110E18] px-4 text-[13.5px] font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.22),0_4px_12px_-2px_rgba(17,14,24,0.45)] transition-all hover:brightness-110 active:scale-[0.98]">Daftar</router-link>
    </div>
    <template v-else>
      <div ref="root" class="relative">
        <button
          type="button"
          class="flex h-9 cursor-pointer items-center gap-2 rounded-full bg-[#14111C]/[0.05] px-3.5 transition-colors hover:bg-[#14111C]/[0.09] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          aria-haspopup="menu"
          :aria-expanded="open"
          @click="open = !open"
        >
          <span class="max-w-[110px] truncate text-[13.5px] font-medium text-[#14111C]">{{ name.split(' ')[0] }}</span>
          <svg class="h-3.5 w-3.5 text-[#5E5A6B] transition-transform duration-200" :class="open ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </button>

        <div v-if="open" role="menu" class="absolute right-0 top-full mt-2 w-72 rounded-[22px] border border-[#E6ECEB] bg-white/95 p-1.5 shadow-[0_20px_48px_-14px_rgba(20,17,28,0.16)] backdrop-blur-md">
          <div class="border-b border-[#E6ECEB] px-3 py-2.5">
            <div class="truncate text-[14px] font-semibold text-[#14111C]">{{ name }}</div>
            <div v-if="email" class="truncate text-[12px] text-[#5E5A6B]">{{ email }}</div>
          </div>

          <div class="py-1">
            <router-link
              v-for="l in menuLinks"
              :key="l.to"
              :to="l.to"
              role="menuitem"
              class="flex h-10 cursor-pointer items-center gap-2.5 rounded-xl px-3 text-[13.5px] font-medium text-[#14111C] transition-colors hover:bg-[#F3F4F6] focus:outline-none"
              @click="open = false"
            >
              <svg v-if="l.to === '/akun'" class="h-4 w-4 shrink-0 text-[#5E5A6B]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z" /></svg>
              <svg v-else class="h-4 w-4 shrink-0 text-[#5E5A6B]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" /></svg>
              <span>{{ l.name }}</span>
            </router-link>

            <router-link
              v-if="!isAdmin"
              to="/billing"
              role="menuitem"
              class="flex h-10 cursor-pointer items-center justify-between gap-2 rounded-xl px-3 text-[13.5px] font-medium text-[#14111C] transition-colors hover:bg-[#F3F4F6] focus:outline-none"
              @click="open = false"
            >
              <span class="flex items-center gap-2.5">
                <svg class="h-4 w-4 shrink-0 text-[#5E5A6B]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z" /></svg>
                <span>Paket &amp; Token</span>
              </span>
              <span class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-semibold tabular-nums" :class="(role || '').toUpperCase() === 'PREMIUM' ? 'bg-[#EBF8F6] text-[#0F766E]' : 'bg-[#F3F4F6] text-[#5E5A6B]'">
                <svg v-if="(role || '').toUpperCase() === 'PREMIUM'" class="h-3 w-3" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2 4.5 13.5H11l-1 8.5L19.5 10.5H13l0-8.5Z" /></svg>
                {{ (role || '').toUpperCase() === 'PREMIUM' ? `PREMIUM · ${balance}` : `GRATIS · ${balance}` }}
              </span>
            </router-link>
          </div>

          <div class="border-t border-[#E6ECEB] pt-1">
            <button
              type="button"
              role="menuitem"
              class="flex h-10 w-full cursor-pointer items-center gap-2.5 rounded-xl px-3 text-[13.5px] font-medium text-[#B91C1C] transition-colors hover:bg-[#FEE2E2]/60 focus:outline-none"
              @click="open = false; $emit('logout')"
            >
              <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" /></svg>
              <span>Keluar</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
