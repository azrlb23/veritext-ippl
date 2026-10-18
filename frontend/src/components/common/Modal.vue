<script setup lang="ts">
import { computed, watch, onUnmounted } from "vue";

interface Props {
  isOpen: boolean;
  title?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl";
  closable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: "",
  maxWidth: "md",
  closable: true,
});

const emit = defineEmits<{
  (e: "close"): void;
}>();

function handleClose() {
  if (props.closable) {
    emit("close");
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.isOpen && props.closable) {
    handleClose();
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (typeof window !== "undefined") {
      if (open) {
        window.addEventListener("keydown", handleKeydown);
        document.body.style.overflow = "hidden";
      } else {
        window.removeEventListener("keydown", handleKeydown);
        document.body.style.overflow = "";
      }
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", handleKeydown);
    document.body.style.overflow = "";
  }
});

const maxWidthClass = computed(() => {
  const map: Record<string, string> = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
  };
  return map[props.maxWidth] || "max-w-md";
});
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 overflow-y-auto"
      role="dialog"
      aria-modal="true"
    >
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-audyr-charcoal/40 backdrop-blur-xs transition-opacity"
        @click="handleClose"
      ></div>

      <!-- Modal container -->
      <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        <div
          class="relative transform overflow-hidden rounded-[18px] bg-white text-left shadow-[0_25px_50px_-12px_rgba(0,0,0,0.12)] transition-all w-full border border-[#ededed] my-8"
          :class="maxWidthClass"
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header || closable"
            class="flex items-center justify-between px-6 py-4 border-b border-[#ededed]"
          >
            <slot name="header">
              <h3 class="text-base font-semibold text-[#262626] tracking-tight">
                {{ title }}
              </h3>
            </slot>
            <button
              v-if="closable"
              type="button"
              @click="handleClose"
              class="rounded-[4px] p-1 text-[#686868] hover:text-[#262626] hover:bg-[#ededed] transition-colors"
              aria-label="Tutup modal"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="px-6 py-5 text-sm text-[#262626]">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="px-6 py-4 bg-[#fafafa] border-t border-[#ededed] flex items-center justify-end space-x-3"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
