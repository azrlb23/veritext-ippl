<script setup lang="ts">
import type { ChatSessionItem } from "../../services/chatService";

defineProps<{ sessions: ChatSessionItem[]; activeId: string | null }>();
defineEmits<{ (e: "open", id: string | null): void; (e: "remove", id: string): void }>();
</script>

<template>
  <div class="flex h-full flex-col">
    <button
      type="button"
      class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
      @click="$emit('open', null)"
    >Percakapan baru</button>

    <p v-if="sessions.length === 0" class="mt-6 px-1 text-[14px] leading-relaxed text-[#5E5A6B]">Percakapan Anda akan tersimpan di sini.</p>
    <ul v-else class="mt-4 flex-1 space-y-1 overflow-y-auto">
      <li v-for="s in sessions" :key="s.id" class="group relative">
        <button
          type="button"
          class="block min-h-[56px] w-full cursor-pointer rounded-[20px] px-4 py-3 pr-12 text-left transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          :class="activeId === s.id ? 'bg-white shadow-lift' : 'hover:bg-white/60'"
          @click="$emit('open', s.id)"
        >
          <span class="block truncate text-[15px] font-semibold text-[#14111C]">{{ s.title }}</span>
          <span class="mt-0.5 block truncate text-[13px] text-[#5E5A6B]">{{ s.last_message || "Belum ada pesan" }}</span>
        </button>
        <button
          type="button"
          class="absolute right-1 top-1/2 flex h-11 w-11 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full text-[#5E5A6B] transition-colors hover:bg-[#FEE2E2] hover:text-[#B91C1C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          :aria-label="`Hapus percakapan ${s.title}`"
          @click="$emit('remove', s.id)"
        >
          <svg viewBox="0 0 20 20" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M5 5l10 10M15 5L5 15" /></svg>
        </button>
      </li>
    </ul>
  </div>
</template>
