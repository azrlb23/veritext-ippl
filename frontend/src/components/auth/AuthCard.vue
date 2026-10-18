<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-6 bg-white p-8 rounded-[14px] border border-[#ededed] shadow-audyr-subtle">
      <!-- Brand & Title -->
      <div class="text-center space-y-2">
        <router-link to="/" class="inline-block">
          <div class="w-9 h-9 rounded-[4px] bg-audyr-ink text-white font-extrabold flex items-center justify-center text-sm mx-auto shadow-audyr-button tracking-tight">
            V
          </div>
        </router-link>
        <h2 class="text-2xl font-extrabold text-audyr-ink tracking-tight">
          {{ title }}
        </h2>
        <p v-if="subtitle" class="text-xs text-audyr-ash">
          {{ subtitle }}
        </p>
      </div>

      <!-- Main Slot / Form -->
      <slot />

      <!-- Footer / Link Slot -->
      <div v-if="$slots.footer" class="text-center text-xs text-audyr-ash pt-3 border-t border-[#ededed]">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
