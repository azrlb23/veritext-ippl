<script setup lang="ts">
import { useNotification } from "../../composables";

const { notifications, dismissNotification } = useNotification();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="notifications.length > 0"
      class="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 max-w-sm w-full pointer-events-none px-4 sm:px-0"
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
          class="pointer-events-auto p-4 rounded-[8px] border shadow-[0_10px_25px_-5px_rgba(0,0,0,0.08)] text-xs flex items-start space-x-3 transition-all duration-300"
          :class="{
            'bg-[#ecfdf5] border-[#a7f3d0] text-[#065f46]': notif.type === 'success',
            'bg-[#fef2f2] border-[#fecaca] text-[#991b1b]': notif.type === 'error',
            'bg-[#fff7ed] border-[#fed7aa] text-[#9a3412]': notif.type === 'warning',
            'bg-white border-[#ededed] text-[#262626]': notif.type === 'info',
          }"
          role="status"
        >
          <span class="text-base font-semibold flex-shrink-0">
            {{
              notif.type === 'success'
                ? '✓'
                : notif.type === 'error'
                ? '✕'
                : notif.type === 'warning'
                ? '⚠'
                : 'ℹ'
            }}
          </span>
          <div class="flex-grow">
            <h6 v-if="notif.title" class="font-semibold text-[#262626] tracking-tight mb-0.5">
              {{ notif.title }}
            </h6>
            <p class="leading-relaxed">{{ notif.message }}</p>
          </div>
          <button
            type="button"
            @click="dismissNotification(notif.id)"
            class="text-[#686868] hover:text-[#262626] p-0.5 rounded-[4px] hover:bg-[#ededed] transition-colors"
            aria-label="Tutup notifikasi"
          >
            ✕
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>
