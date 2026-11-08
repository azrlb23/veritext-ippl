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
  <div class="items-center gap-1.5">
    <template v-if="isGuest">
      <router-link
        to="/login"
        class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] transition-colors duration-200 hover:bg-[#14111C]/[0.05] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
      >Masuk</router-link>
      <router-link
        to="/register"
        class="inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-6 text-[14px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
      >Daftar gratis</router-link>
    </template>
    <template v-else>
      <span v-if="!isAdmin" class="inline-flex h-10 items-center rounded-full bg-[#F3EEFA] px-4 text-[13px] font-semibold tabular-nums text-[#6D28D9]">
        {{ balance }} token
      </span>
      <div ref="root" class="relative">
        <button
          type="button"
          class="flex h-11 cursor-pointer items-center gap-2.5 rounded-full bg-[#14111C]/[0.05] pl-1.5 pr-4 transition-colors hover:bg-[#14111C]/[0.08] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          aria-haspopup="menu"
          :aria-expanded="open"
          @click="open = !open"
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#8A3FE0] to-[#D26BE6] text-[13px] font-semibold text-white">
            {{ name.charAt(0).toUpperCase() }}
          </span>
          <span class="max-w-[110px] truncate text-[13.5px] font-medium text-[#14111C]">{{ name }}</span>
        </button>
        <div v-if="open" role="menu" class="absolute right-0 top-full mt-2 w-56 rounded-[24px] bg-white p-2 shadow-float">
          <router-link
            v-for="l in menuLinks"
            :key="l.to"
            :to="l.to"
            role="menuitem"
            class="flex h-11 cursor-pointer items-center rounded-[16px] px-4 text-[15px] font-medium text-[#14111C] transition-colors hover:bg-[#F3EEFA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            @click="open = false"
          >{{ l.name }}</router-link>
          <button
            type="button"
            role="menuitem"
            class="flex h-11 w-full cursor-pointer items-center rounded-[16px] px-4 text-[15px] font-medium text-[#5E5A6B] transition-colors hover:bg-[#F3EEFA] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
            @click="open = false; $emit('logout')"
          >Keluar</button>
        </div>
      </div>
    </template>
  </div>
</template>
