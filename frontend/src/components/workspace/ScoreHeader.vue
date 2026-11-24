<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";

const props = defineProps<{
  title?: string | null;
  composite: number;
  lexical?: number | null;
  semantic?: number | null;
  stylometric?: number | null;
  exporting?: boolean;
}>();
const emit = defineEmits<{ (e: "download"): void }>();
const router = useRouter();
const authStore = useAuthStore();

const verdict = computed(() =>
  props.composite <= 20
    ? { text: "Aman", tone: "text-[#047857]" }
    : props.composite <= 40
      ? { text: "Perlu ditinjau", tone: "text-[#B45309]" }
      : { text: "Perlu direvisi", tone: "text-[#B91C1C]" },
);
const isFree = computed(() => authStore.role === "FREE");
const fmt = (n?: number | null) => (n === null || n === undefined ? "-" : `${n.toFixed(0)}%`);
const parts = computed(() => [
  { label: "Kata sama", value: fmt(props.lexical) },
  { label: "Makna sama", value: fmt(props.semantic) },
  { label: "Pola tulisan AI", value: fmt(props.stylometric) },
]);

function download() {
  if (isFree.value) return router.push("/billing");
  emit("download");
}
</script>

<template>
  <header class="rounded-[36px] border border-[#E8ECEB] bg-white p-6 shadow-float sm:p-9">
    <router-link
      to="/riwayat"
      aria-label="Kembali ke Riwayat"
      title="Kembali ke Riwayat"
      class="vt-btn-light inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-full hover:-translate-x-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6" /></svg>
    </router-link>
    <div class="mt-2 grid gap-7 lg:grid-cols-[1fr_auto] lg:items-end">
      <div class="min-w-0">
        <h1 class="truncate text-[22px] font-semibold tracking-[-0.03em] text-[#14111C] sm:text-[28px]">{{ title || "Naskah" }}</h1>
        <p class="mt-3 flex flex-wrap items-baseline gap-x-4">
          <span class="text-[88px] font-semibold leading-none tracking-[-0.06em] tabular-nums text-[#14111C] sm:text-[112px]">{{ composite.toFixed(0) }}<span class="text-[40px] tracking-[-0.04em]">%</span></span>
          <span class="text-[18px] font-semibold" :class="verdict.tone">{{ verdict.text }}</span>
        </p>
        <p class="text-[14px] text-[#5E5A6B]">kemiripan keseluruhan</p>
      </div>
      <div class="flex flex-col gap-4 lg:items-end">
        <dl class="grid grid-cols-3 gap-5 border-t border-[#E8ECEB] pt-5 sm:gap-8 lg:border-t-0 lg:pt-0">
          <div v-for="p in parts" :key="p.label">
            <dd class="text-[26px] font-semibold leading-none tracking-[-0.03em] tabular-nums text-[#14111C]">{{ p.value }}</dd>
            <dt class="mt-2 text-[13px] text-[#5E5A6B]">{{ p.label }}</dt>
          </div>
        </dl>
        <button
          type="button"
          :disabled="exporting"
          class="vt-btn-dark inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:opacity-40 lg:w-auto"
          @click="download"
        >{{ exporting ? "Menyiapkan..." : isFree ? "Unduh PDF (Premium)" : "Unduh sertifikat PDF" }}</button>
      </div>
    </div>
  </header>
</template>
