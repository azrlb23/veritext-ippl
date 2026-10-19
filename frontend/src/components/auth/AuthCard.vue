<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-6 bg-white p-8 sm:p-10 rounded-[24px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)]">
      <!-- Brand & Title -->
      <div class="text-center space-y-2.5">
        <router-link to="/" class="inline-block">
          <div class="w-10 h-10 rounded-full bg-[#17191c] text-white font-semibold flex items-center justify-center text-sm mx-auto shadow-sm tracking-tight">
            V
          </div>
        </router-link>
        <h2 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight">
          {{ title }}
        </h2>
        <p v-if="subtitle" class="text-xs text-[#777b86] font-normal">
          {{ subtitle }}
        </p>
      </div>

      <!-- Main Slot / Form -->
      <slot />

      <!-- Footer / Link Slot -->
      <div v-if="$slots.footer" class="text-center text-xs text-[#777b86] pt-4 border-t border-[#ededed]">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
