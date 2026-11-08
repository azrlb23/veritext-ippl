<script setup lang="ts">
interface Props {
  icon?: string;
  title: string;
  description?: string;
  actionText?: string;
}

withDefaults(defineProps<Props>(), {
  icon: "",
  description: "",
  actionText: "",
});

const emit = defineEmits<{
  (e: "action"): void;
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-[20px] border border-dashed border-[#CBD5E1] bg-[#F8FAFC] space-y-3 font-sans select-none">
    <div
      v-if="icon || $slots.icon"
      class="w-11 h-11 rounded-full bg-white border border-[#E4E8F0] shadow-2xs flex items-center justify-center text-sm text-[#5B6475]"
    >
      <slot name="icon">{{ icon }}</slot>
    </div>

    <div class="space-y-1 max-w-sm">
      <h4 class="text-sm font-bold text-[#0B0F19] tracking-tight">
        {{ title }}
      </h4>
      <p v-if="description" class="text-xs text-[#5B6475] leading-relaxed font-normal">
        {{ description }}
      </p>
    </div>

    <div v-if="actionText || $slots.action" class="pt-2">
      <slot name="action">
        <button
          type="button"
          @click="emit('action')"
          class="px-5 py-2 bg-[#1560BD] hover:bg-[#1A73D9] text-white rounded-full text-xs font-semibold tracking-tight shadow-sm transition-all active:scale-[0.98] cursor-pointer"
        >
          {{ actionText }}
        </button>
      </slot>
    </div>
  </div>
</template>
