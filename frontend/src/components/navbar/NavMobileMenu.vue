<script setup lang="ts">
interface LinkItem { name: string; to: string }
defineProps<{ links: LinkItem[]; isActive: (to: string) => boolean; isGuest: boolean; isAdmin: boolean; name: string; balance: number }>();
defineEmits<{ (e: "close"): void; (e: "logout"): void }>();
</script>

<template>
  <div id="menu-navigasi" class="absolute inset-x-0 top-full mt-2 rounded-[30px] bg-white/90 p-3 shadow-float backdrop-blur-2xl">
    <nav class="flex flex-col gap-1" aria-label="Navigasi utama">
      <router-link
        v-for="item in links"
        :key="item.to"
        :to="item.to"
        :aria-current="isActive(item.to) ? 'page' : undefined"
        class="flex h-12 cursor-pointer items-center rounded-[18px] px-4 text-[16px] font-medium transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        :class="isActive(item.to) ? 'bg-[#F3EEFA] text-[#14111C]' : 'text-[#4B4757] hover:bg-[#14111C]/[0.04]'"
        @click="$emit('close')"
      >
        {{ item.name }}
      </router-link>
    </nav>

    <div class="mt-3 flex flex-col gap-2 border-t border-[#14111C]/[0.06] px-1 pt-3 sm:flex-row sm:items-center">
      <template v-if="isGuest">
        <router-link
          to="/login"
          class="inline-flex h-12 w-full cursor-pointer sm:flex-1 items-center justify-center rounded-full bg-[#14111C]/[0.05] text-[15px] font-semibold text-[#14111C] transition-colors duration-200 hover:bg-[#14111C]/[0.08]"
          @click="$emit('close')"
        >Masuk</router-link>
        <router-link
          to="/register"
          class="inline-flex h-12 w-full cursor-pointer sm:flex-1 items-center justify-center rounded-full bg-[#14111C] text-[15px] font-semibold text-white shadow-btn-dark"
          @click="$emit('close')"
        >Daftar gratis</router-link>
      </template>
      <template v-else>
        <div class="flex items-center gap-3 px-2 sm:flex-1">
          <span class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#8A3FE0] to-[#D26BE6] text-[15px] font-semibold text-white">
            {{ name.charAt(0).toUpperCase() }}
          </span>
          <div class="min-w-0">
            <div class="truncate text-[15px] font-semibold text-[#14111C]">{{ name }}</div>
            <div v-if="!isAdmin" class="text-[13px] font-medium tabular-nums text-[#6D28D9]">{{ balance }} token</div>
          </div>
        </div>
        <button
          type="button"
          class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C]/[0.05] px-6 sm:w-auto text-[15px] font-semibold text-[#14111C] transition-colors duration-200 hover:bg-[#14111C]/[0.08]"
          @click="$emit('logout')"
        >Keluar</button>
      </template>
    </div>
  </div>
</template>
