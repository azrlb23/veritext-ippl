<script setup lang="ts">
import { onMounted } from "vue";
import { useAdminData, useSectionReveal } from "../composables";
import { GlobalAnalyticsCards, RoleDistribution, TrendChart } from "../components/admin";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { loading, error, analytics, overviewExtras, health, fetchOverview } = useAdminData();

const isHealthy = (s?: string) => ["HEALTHY", "OPERATIONAL", "RUNNING"].includes((s || "").toUpperCase());
const num = (n: number) => (n || 0).toLocaleString("id-ID");

onMounted(() => {
  void fetchOverview();
});
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Kondisi sistem, hanya dibaca.
      </h1>
      <button type="button" :disabled="loading" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-50" @click="fetchOverview">
        {{ loading ? "Memuat..." : "Muat ulang" }}
      </button>
    </div>

    <div v-if="error && !loading" class="vt-reveal mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ error }}</p>
      <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold" @click="fetchOverview">Coba lagi</button>
    </div>

    <div class="space-y-6">
      <div class="vt-reveal vt-d-1"><GlobalAnalyticsCards :data="analytics" :loading="loading" /></div>

      <section class="vt-reveal vt-d-2 rounded-[32px] bg-white p-7 shadow-float" aria-label="Metrik aktivitas tambahan" :aria-busy="loading">
        <dl class="grid grid-cols-1 gap-6 divide-[#E8ECEB] sm:grid-cols-3 sm:gap-0 sm:divide-x">
          <div class="sm:pr-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#14111C]">{{ loading ? "-" : num(overviewExtras.new_users_7d) }}</dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">pengguna baru 7 hari</dt>
          </div>
          <div class="sm:px-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#14111C]">{{ loading ? "-" : num(overviewExtras.audits_today) }}</dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">pemeriksaan hari ini</dt>
          </div>
          <div class="sm:pl-6">
            <dd class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#0F766E]">{{ loading ? "-" : num(overviewExtras.tokens_spent_30d) }}</dd>
            <dt class="mt-2 text-[14px] text-[#5E5A6B]">token terpakai 30 hari</dt>
          </div>
        </dl>
      </section>

      <div class="vt-reveal vt-d-3 grid gap-6 xl:grid-cols-3">
        <TrendChart :trends="overviewExtras.trends" :loading="loading" class="xl:col-span-2" />
        <RoleDistribution :distribution="overviewExtras.role_distribution" :loading="loading" />
      </div>

      <div class="vt-reveal vt-d-4 flex flex-wrap items-center justify-between gap-3 rounded-[28px] bg-white px-7 py-4 shadow-float">
        <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-[14px] text-[#4B4757]">
          <span>
            Basis Data:
            <strong class="ml-1 font-semibold" :class="loading ? 'text-[#14111C]' : isHealthy(health.database_status) ? 'text-[#0F766E]' : 'text-[#B91C1C]'">
              {{ loading ? "-" : isHealthy(health.database_status) ? "Normal" : "Terganggu" }}
            </strong>
          </span>
          <span>
            Antrean Pemeriksaan:
            <strong class="ml-1 font-semibold" :class="loading ? 'text-[#14111C]' : isHealthy(health.redis_status) ? 'text-[#0F766E]' : 'text-[#B91C1C]'">
              {{ loading ? "-" : isHealthy(health.redis_status) ? "Normal" : "Terganggu" }}
            </strong>
          </span>
        </div>
        <router-link to="/admin/sistem" class="text-[14px] font-semibold text-[#0F766E] hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]">Lihat detail sistem</router-link>
      </div>
    </div>
  </div>
</template>
