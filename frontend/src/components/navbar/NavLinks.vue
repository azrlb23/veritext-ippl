<script setup lang="ts">
interface LinkItem { name: string; to: string }
defineProps<{ links: LinkItem[]; isActive: (to: string) => boolean }>();
</script>

<template>
  <nav class="flex items-center gap-5" aria-label="Navigasi utama">
    <router-link
      v-for="item in links"
      :key="item.to"
      :to="item.to"
      class="inline-flex h-9 items-center text-[13.5px] transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
      :class="isActive(item.to) ? 'font-semibold text-[#14111C]' : 'font-medium text-[#5E5A6B] hover:text-[#14111C]'"
    >
      {{ item.name }}
    </router-link>
  </nav>
</template>
