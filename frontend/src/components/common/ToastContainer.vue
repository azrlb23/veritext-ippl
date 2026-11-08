<script setup lang="ts">
import { useNotification } from "../../composables";

const { notifications, dismissNotification } = useNotification();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="notifications.length > 0"
      class="fixed bottom-4 right-0 z-50 flex w-full max-w-sm flex-col space-y-2.5 px-4 pointer-events-none sm:bottom-6 sm:right-6 sm:px-0"
      role="region"
      aria-label="Notifikasi Sistem"
    >
      <transition-group
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-for="notif in notifications"
          :key="notif.id"
          class="pointer-events-auto flex items-start space-x-3 rounded-[22px] bg-white p-4 text-[13px] text-[#14111C] shadow-float transition-all duration-300"
          role="status"
        >
          <span class="flex-shrink-0 pt-0.5">
            <svg v-if="notif.type === 'success'" class="w-4 h-4 text-[#15803D]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else-if="notif.type === 'warning'" class="w-4 h-4 text-[#ea580c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else-if="notif.type === 'error'" class="w-4 h-4 text-[#dc2626]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <svg v-else class="w-4 h-4 text-[#8A3FE0]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
          <div class="flex-grow">
            <h6 v-if="notif.title" class="mb-0.5 font-semibold tracking-tight text-[#14111C]">
              {{ notif.title }}
            </h6>
            <p class="leading-relaxed text-[#4B4757]">{{ notif.message }}</p>
          </div>
          <button
            type="button"
            @click="dismissNotification(notif.id)"
            class="cursor-pointer rounded-full p-1 text-[#5E5A6B] transition-all hover:bg-[#F3EEFA] hover:text-[#14111C]"
            aria-label="Tutup notifikasi"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>
