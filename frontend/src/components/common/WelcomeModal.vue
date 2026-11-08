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
  if (e.key === "Escape" && props.isOpen) handleClose();
}

watch(() => props.isOpen, (open) => {
  clearTimer();
  if (typeof window === "undefined") return;
  if (open) {
    window.addEventListener("keydown", onKeydown);
    document.body.style.overflow = "hidden";
    timer = setTimeout(handleClose, 4000);
    nextTick(() => continueBtn.value?.focus());
  } else {
    window.removeEventListener("keydown", onKeydown);
    document.body.style.overflow = "";
  }
}, { immediate: true });

onUnmounted(() => {
  clearTimer();
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", onKeydown);
    document.body.style.overflow = "";
  }
});
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out motion-reduce:transition-none"
      enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in motion-reduce:transition-none"
      leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95"
    >
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="welcome-title">
        <div class="fixed inset-0 bg-[#0B0F19]/40 backdrop-blur-xs" @click="handleClose" />
        <div class="relative w-full max-w-sm rounded-[24px] bg-white p-6 shadow-[0_20px_50px_rgba(11,15,25,0.16)] border border-[#E4E8F0] z-10 text-center font-sans transform motion-reduce:transform-none">
          <h3 id="welcome-title" class="text-lg font-bold text-[#0B0F19] tracking-tight">Selamat Datang, {{ name }}</h3>
          <p class="mt-2 text-sm text-[#5B6475] leading-relaxed">
            {{ role === "ADMIN" ? "Panel pemantauan sistem VeriText AI siap digunakan." : "Sistem siap mengaudit orisinalitas naskah Anda." }}
          </p>
          <div class="mt-5 flex justify-center">
            <button
              ref="continueBtn"
              type="button"
              @click="handleClose"
              class="px-6 py-2.5 rounded-full bg-[#1560BD] hover:bg-[#114c97] text-white text-sm font-semibold shadow-sm transition-colors active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1560BD] focus-visible:ring-offset-2 cursor-pointer"
            >
              Lanjutkan
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
