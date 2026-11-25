<script setup lang="ts">
import { ref, watch, onUnmounted, nextTick } from "vue";

interface Props { isOpen: boolean; name: string; role?: string; }
const props = withDefaults(defineProps<Props>(), { role: "FREE" });
const emit = defineEmits<{ (e: "close"): void }>();
const continueBtn = ref<HTMLButtonElement | null>(null);
let timer: ReturnType<typeof setTimeout> | null = null;

function clearTimer() {
  if (timer) { clearTimeout(timer); timer = null; }
}

function handleClose() {
  clearTimer();
  emit("close");
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") handleClose();
}

watch(() => props?.isOpen, (open) => {
  clearTimer();
  if (typeof window === "undefined") return;
  if (open) {
    window.addEventListener("keydown", onKeydown);
    timer = setTimeout(handleClose, 3500);
    nextTick(() => continueBtn.value?.focus());
  } else {
    window.removeEventListener("keydown", onKeydown);
  }
}, { immediate: true });

onUnmounted(() => {
  clearTimer();
  if (typeof window !== "undefined") window.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out motion-reduce:transition-none"
      enter-from-class="opacity-0 -translate-y-3" enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in motion-reduce:transition-none"
      leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-3"
    >
      <div v-if="isOpen" class="pointer-events-none fixed inset-x-0 top-6 z-50 flex justify-center px-4" role="status" aria-live="polite">
        <div class="pointer-events-auto flex items-center gap-3 rounded-full border border-[#E8ECEB] bg-white/95 py-2 pl-4 pr-2 font-sans shadow-float backdrop-blur-md">
          <svg class="h-4 w-4 flex-shrink-0 text-[#0F766E]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <p class="truncate text-[14px] font-medium tracking-[-0.01em] text-[#14111C]">Selamat datang, {{ name }}</p>
          <button
            ref="continueBtn"
            type="button"
            aria-label="Tutup sambutan"
            class="inline-flex h-7 w-7 flex-shrink-0 cursor-pointer items-center justify-center rounded-full text-[#5E5A6B] transition hover:bg-[#F4F6F5] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
            @click="handleClose"
          >
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
