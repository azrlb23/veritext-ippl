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
  <div class="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-[14px] border border-dashed border-[#ededed] bg-[#fafafa] space-y-3">
    <div
      v-if="icon || $slots.icon"
      class="w-10 h-10 rounded-[6px] bg-white border border-[#ededed] shadow-sm flex items-center justify-center text-sm text-[#262626]"
    >
      <slot name="icon">{{ icon }}</slot>
    </div>

    <div class="space-y-1 max-w-sm">
      <h4 class="text-sm font-semibold text-[#262626] tracking-tight">
        {{ title }}
      </h4>
      <p v-if="description" class="text-xs text-[#686868] leading-relaxed font-normal">
        {{ description }}
      </p>
    </div>

    <div v-if="actionText || $slots.action" class="pt-2">
      <slot name="action">
        <button
          type="button"
          @click="emit('action')"
          class="px-4 py-2 bg-[#262626] hover:bg-[#171717] text-white rounded-[4px] text-xs font-medium tracking-tight shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] transition-all"
        >
          {{ actionText }}
        </button>
      </slot>
    </div>
  </div>
</template>
