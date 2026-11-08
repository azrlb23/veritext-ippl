<script setup lang="ts">
defineProps<{ isGuest: boolean; isAdmin: boolean; name: string; balance: number }>();
defineEmits<{ (e: "logout"): void }>();
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
      <span class="flex h-10 items-center gap-2.5 rounded-full bg-[#14111C]/[0.05] pl-1 pr-4">
        <span class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#8A3FE0] to-[#D26BE6] text-[13px] font-semibold text-white">
          {{ name.charAt(0).toUpperCase() }}
        </span>
        <span class="max-w-[110px] truncate text-[13.5px] font-medium text-[#14111C]">{{ name }}</span>
      </span>
      <button
        type="button"
        class="inline-flex h-11 cursor-pointer items-center rounded-full px-4 text-[14px] font-medium text-[#5E5A6B] transition-colors duration-200 hover:bg-[#14111C]/[0.05] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        @click="$emit('logout')"
      >Keluar</button>
    </template>
  </div>
</template>
