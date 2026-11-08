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
        <div class="fixed inset-0 bg-[#14111C]/30 backdrop-blur-sm" @click="handleClose" />
        <div class="relative z-10 w-full max-w-[400px] rounded-[36px] bg-white p-8 text-center font-sans shadow-float sm:p-10">
          <h3 id="welcome-title" class="text-[30px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#14111C]">
            Selamat datang,
            <span class="vt-accent block truncate pb-1">{{ name }}</span>
          </h3>
          <p class="mx-auto mt-4 max-w-[280px] text-[15px] leading-[1.65] text-[#4B4757]">
            {{ role === "ADMIN" ? "Panel pemantauan sistem VeriText AI siap digunakan." : "Sistem siap memeriksa orisinalitas naskah Anda." }}
          </p>
          <button
            ref="continueBtn"
            type="button"
            class="mt-7 inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
            @click="handleClose"
          >
            Lanjutkan
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
