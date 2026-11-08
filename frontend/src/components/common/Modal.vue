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
        class="fixed inset-0 bg-[#0B0F19]/40 backdrop-blur-xs transition-opacity"
        @click="handleClose"
      ></div>

      <!-- Modal container -->
      <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        <div
          class="relative transform overflow-hidden rounded-[28px] bg-white text-left shadow-[0_20px_50px_rgba(11,15,25,0.16)] transition-all w-full border border-[#E4E8F0] my-8 font-sans"
          :class="maxWidthClass"
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header || closable"
            class="flex items-center justify-between px-6 py-4 border-b border-[#E4E8F0]"
          >
            <slot name="header">
              <h3 class="text-base font-bold text-[#0B0F19] tracking-tight">
                {{ title }}
              </h3>
            </slot>
            <button
              v-if="closable"
              type="button"
              @click="handleClose"
              class="rounded-full p-1.5 text-[#5B6475] hover:text-[#0B0F19] hover:bg-[#F3F6FC] transition-colors cursor-pointer active:scale-[0.95]"
              aria-label="Tutup modal"
            >
              <svg class="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="px-6 py-5 text-sm text-[#0B0F19]">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="px-6 py-4 bg-[#F8FAFC] border-t border-[#E4E8F0] flex items-center justify-end space-x-3"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
