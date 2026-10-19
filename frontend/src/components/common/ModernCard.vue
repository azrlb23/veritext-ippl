<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    subtitle?: string;
    timestamp?: string;
    statValue?: string;
    statLabel?: string;
    actionLabel?: string;
    actionTo?: string;
    isSaved?: boolean;
    showSaveButton?: boolean;
  }>(),
  {
    isSaved: false,
    showSaveButton: true,
    actionLabel: "Uji Coba",
  }
);

defineEmits<{
  (e: "toggleSave"): void;
  (e: "actionClick"): void;
}>();
</script>

<template>
  <div
    class="bg-white rounded-[24px] p-6 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out flex flex-col justify-between group"
  >
    <div>
      <!-- Top Row: Icon Avatar + Save Pill -->
      <div class="flex items-center justify-between mb-4">
        <!-- Circular Icon Slot -->
        <div class="w-10 h-10 rounded-full flex items-center justify-center border border-[#ededed] bg-[#fafafb] text-[#17191c] transition-transform duration-150 group-hover:scale-105">
          <slot name="icon">
            <svg class="w-4 h-4 text-[#17191c]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </slot>
        </div>

        <!-- Save / Action Pill -->
        <button
          v-if="showSaveButton"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-medium tracking-tight transition-colors duration-150 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]"
          :class="isSaved ? 'bg-[#17191c] border-[#17191c] text-white' : 'bg-transparent border-[#ededed] text-[#17191c] hover:bg-[#f2f2f3]'"
          @click="$emit('toggleSave')"
        >
          <span>{{ isSaved ? 'Tersimpan' : 'Simpan' }}</span>
          <svg class="w-3.5 h-3.5" :fill="isSaved ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
        </button>
      </div>

      <!-- Subtitle + Timestamp -->
      <div v-if="subtitle" class="flex items-center text-xs font-medium text-[#777b86]">
        <span>{{ subtitle }}</span>
        <span v-if="timestamp" class="text-[#979799] font-normal ml-1.5 text-[11px]">{{ timestamp }}</span>
      </div>

      <!-- Main Title -->
      <h3 v-if="title" class="text-base font-semibold text-[#17191c] tracking-tight mt-0.5">
        {{ title }}
      </h3>

      <!-- Tags Slot -->
      <div v-if="$slots.tags" class="flex flex-wrap gap-1.5 mt-3">
        <slot name="tags" />
      </div>

      <!-- Default Body / Description Slot -->
      <div class="text-xs text-[#777b86] leading-relaxed mt-3.5">
        <slot />
      </div>
    </div>

    <!-- Bottom Row: Stat on Left + Dark Pill Button on Right -->
    <div v-if="statValue || $slots.footer" class="pt-4 mt-5 border-t border-[#ededed] flex items-center justify-between">
      <slot name="footer">
        <div>
          <div class="text-sm font-semibold text-[#17191c] tabular-nums">
            {{ statValue }}
          </div>
          <div v-if="statLabel" class="text-[10px] text-[#777b86] font-medium">
            {{ statLabel }}
          </div>
        </div>

        <router-link
          v-if="actionTo"
          :to="actionTo"
          class="px-4 py-1.5 bg-[#17191c] hover:bg-[#2e3138] text-white text-xs font-medium rounded-full active:scale-[0.98] transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]"
        >
          {{ actionLabel }}
        </router-link>
        <button
          v-else
          type="button"
          class="px-4 py-1.5 bg-[#17191c] hover:bg-[#2e3138] text-white text-xs font-medium rounded-full active:scale-[0.98] transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]"
          @click="$emit('actionClick')"
        >
          {{ actionLabel }}
        </button>
      </slot>
    </div>
  </div>
</template>
