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
    class="bg-white rounded-[14px] p-6 border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] hover:border-[#d4d4d4] transition-all duration-150 ease-out flex flex-col justify-between group"
  >
    <div>
      <!-- Top Row: Icon Avatar + Save Pill -->
      <div class="flex items-center justify-between mb-4">
        <!-- Circular Icon Slot -->
        <div class="w-10 h-10 rounded-full flex items-center justify-center border border-[#ededed] bg-white text-[#262626] transition-transform duration-150 group-hover:scale-105">
          <slot name="icon">
            <span class="w-2 h-2 rounded-full bg-[#262626]"></span>
          </slot>
        </div>

        <!-- Save / Action Pill -->
        <button
          v-if="showSaveButton"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-[4px] border text-xs font-medium tracking-tight transition-colors duration-150 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]"
          :class="isSaved ? 'bg-[#262626] border-[#262626] text-white' : 'bg-transparent border-[#ededed] text-[#262626] hover:bg-[#fafafa]'"
          @click="$emit('toggleSave')"
        >
          <span>{{ isSaved ? 'Tersimpan' : 'Simpan' }}</span>
          <svg class="w-3.5 h-3.5" :fill="isSaved ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
        </button>
      </div>

      <!-- Subtitle + Timestamp -->
      <div v-if="subtitle" class="flex items-center text-xs font-medium text-[#515151]">
        <span>{{ subtitle }}</span>
        <span v-if="timestamp" class="text-[#929292] font-normal ml-1.5 text-[11px]">{{ timestamp }}</span>
      </div>

      <!-- Main Title -->
      <h3 v-if="title" class="text-base font-semibold text-[#262626] tracking-tight mt-0.5">
        {{ title }}
      </h3>

      <!-- Tags Slot -->
      <div v-if="$slots.tags" class="flex flex-wrap gap-1.5 mt-3">
        <slot name="tags" />
      </div>

      <!-- Default Body / Description Slot -->
      <div class="text-xs text-[#686868] leading-relaxed mt-3.5">
        <slot />
      </div>
    </div>

    <!-- Bottom Row: Stat on Left + Dark Pill Button on Right -->
    <div v-if="statValue || $slots.footer" class="pt-4 mt-5 border-t border-[#ededed] flex items-center justify-between">
      <slot name="footer">
        <div>
          <div class="text-sm font-semibold font-mono text-[#262626] tabular-nums">
            {{ statValue }}
          </div>
          <div v-if="statLabel" class="text-[10px] text-[#737373] font-medium">
            {{ statLabel }}
          </div>
        </div>

        <router-link
          v-if="actionTo"
          :to="actionTo"
          class="px-3.5 py-1.5 bg-[#262626] hover:bg-[#171717] text-white text-xs font-medium rounded-[4px] shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] active:scale-[0.98] transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]"
        >
          {{ actionLabel }}
        </router-link>
        <button
          v-else
          type="button"
          class="px-3.5 py-1.5 bg-[#262626] hover:bg-[#171717] text-white text-xs font-medium rounded-[4px] shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] active:scale-[0.98] transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626]"
          @click="$emit('actionClick')"
        >
          {{ actionLabel }}
        </button>
      </slot>
    </div>
  </div>
</template>
