<script setup lang="ts">
import { onMounted } from "vue";
import { useAdminData, useSectionReveal } from "../composables";
import { SystemHealthPanel } from "../components/admin";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { loading, error, health, systemExtras, fetchSystem } = useAdminData();

const num = (n: number) => (n || 0).toLocaleString("id-ID");

onMounted(() => {
  void fetchSystem();
});
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1180px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Kondisi infrastruktur sistem.
      </h1>
      <button type="button" :disabled="loading" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-50" @click="fetchSystem">
        {{ loading ? "Memuat..." : "Muat ulang" }}
      </button>
    </div>

    <div v-if="error && !loading" class="vt-reveal mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ error }}</p>
      <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold" @click="fetchSystem">Coba lagi</button>
    </div>

    <div class="space-y-6">
      <div class="vt-reveal vt-d-1"><SystemHealthPanel :health="health" :loading="loading" /></div>

      <section class="vt-reveal vt-d-2 rounded-[32px] bg-white p-7 shadow-float" aria-label="Ringkasan antrean dan kesehatan 24 jam" :aria-busy="loading">
        <dl class="grid grid-cols-1 gap-6 divide-[#E8ECEB] sm:grid-cols-3 sm:gap-0 sm:divide-x">
          <div class="sm:pr-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums" :class="!loading && systemExtras.failed_audits_24h > 0 ? 'text-[#B91C1C]' : 'text-[#14111C]'">
              {{ loading ? "-" : num(systemExtras.failed_audits_24h) }}
            </dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">audit gagal 24 jam</dt>
          </div>
          <div class="sm:px-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#0F766E]">
              {{ loading ? "-" : num(systemExtras.processing_audits) }}
            </dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">sedang diproses</dt>
          </div>
          <div class="sm:pl-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#14111C]">
              {{ loading ? "-" : num(systemExtras.queued_audits) }}
            </dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">dalam antrean</dt>
          </div>
        </dl>
      </section>
    </div>
  </div>
</template>
