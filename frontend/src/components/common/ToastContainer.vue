<script setup lang="ts">
import { useNotification } from "../../composables";

const { notifications, dismissNotification } = useNotification();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="notifications.length > 0"
      class="pointer-events-none fixed inset-x-0 top-6 z-50 flex flex-col items-center space-y-2 px-4"
      role="region"
      aria-label="Notifikasi Sistem"
    >
      <transition-group
        enter-active-class="transition duration-200 ease-out motion-reduce:transition-none"
        enter-from-class="opacity-0 -translate-y-3"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in motion-reduce:transition-none"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-3"
      >
        <div
          v-for="notif in notifications"
          :key="notif.id"
          class="pointer-events-auto flex items-center gap-3 rounded-full border border-[#E8ECEB] bg-white/95 py-2 pl-4 pr-2 font-sans shadow-float backdrop-blur-md transition-all"
          role="status"
        >
          <!-- Polos tanpa outline/background -->
          <svg v-if="notif.type === 'success'" class="h-4 w-4 flex-shrink-0 text-[#0F766E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="notif.type === 'warning'" class="h-4 w-4 flex-shrink-0 text-[#D97706]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <svg v-else-if="notif.type === 'error'" class="h-4 w-4 flex-shrink-0 text-[#E11D48]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else class="h-4 w-4 flex-shrink-0 text-[#0F766E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          <p class="truncate text-[14px] font-medium tracking-[-0.01em] text-[#14111C]">
            {{ notif.message }}
          </p>

          <button
            type="button"
            @click="dismissNotification(notif.id)"
            class="inline-flex h-7 w-7 flex-shrink-0 cursor-pointer items-center justify-center rounded-full text-[#5E5A6B] transition hover:bg-[#F4F6F5] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            aria-label="Tutup notifikasi"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>
