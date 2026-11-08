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
  <header class="rounded-[36px] bg-white p-6 shadow-float sm:p-9">
    <router-link to="/riwayat" class="inline-flex h-11 cursor-pointer items-center text-[14px] font-medium text-[#5E5A6B] transition-colors hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]">&larr; Riwayat</router-link>
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
        <dl class="grid grid-cols-3 gap-5 rounded-[24px] bg-[#F3EEFA] p-5 sm:gap-8">
          <div v-for="p in parts" :key="p.label">
            <dd class="text-[26px] font-semibold leading-none tracking-[-0.03em] tabular-nums text-[#14111C]">{{ p.value }}</dd>
            <dt class="mt-2 text-[13px] text-[#5E5A6B]">{{ p.label }}</dt>
          </div>
        </dl>
        <button
          type="button"
          :disabled="exporting"
          class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:opacity-40 lg:w-auto"
          @click="download"
        >{{ exporting ? "Menyiapkan..." : isFree ? "Unduh PDF (Premium)" : "Unduh sertifikat PDF" }}</button>
      </div>
    </div>
  </header>
</template>
