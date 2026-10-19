<script setup lang="ts">
import { ref } from "vue";

interface TierCardItem {
  tierId: string;
  category: string;
  engine: string;
  title: string;
  tags: string[];
  description: string;
  statValue: string;
  statLabel: string;
  iconBg: string;
  iconColor: string;
  accentBorder: string;
  badgeHex: string;
  isSaved: boolean;
}

const tiers = ref<TierCardItem[]>([
  {
    tierId: "T1",
    category: "Leksikal Engine",
    engine: "Rabin-Karp 64b",
    title: "Winnowing Fingerprint",
    tags: ["k=5, w=4", "Verbatim Match", "Bobot 50%"],
    description: "Ekstraksi k-gram dan sidik jari hash leksikal untuk mendeteksi penjiplakan salin-tempel langsung kata demi kata secara presisi.",
    statValue: "100% Akurat",
    statLabel: "Hashing Verbatim · Latensi < 10ms",
    iconBg: "bg-rose-50",
    iconColor: "text-rose-600",
    accentBorder: "border-rose-100",
    badgeHex: "#EF4444",
    isSaved: true,
  },
  {
    tierId: "T2",
    category: "Semantik Engine",
    engine: "MiniLM-L12-v2",
    title: "pgvector HNSW Cosine",
    tags: ["384 Dimensi", "Jarak Kosinus", "Bobot 35%"],
    description: "Model representasi embedding dense untuk menangkap parafrasa cerdas dan substitusi sinonim yang lolos dari filter kata.",
    statValue: "384 Dimensi",
    statLabel: "HNSW ANN Search · Latensi < 1.500ms",
    iconBg: "bg-orange-50",
    iconColor: "text-orange-600",
    accentBorder: "border-orange-100",
    badgeHex: "#F97316",
    isSaved: true,
  },
  {
    tierId: "T3",
    category: "Stilometri AI",
    engine: "Analisis Pola Sintaksis",
    title: "Pola & Sintaksis LLM",
    tags: ["Burstiness", "Type-Token Ratio", "Bobot 15%"],
    description: "Mengevaluasi varians panjang kalimat dan kekayaan leksikal guna mendeteksi naskah yang digenerasi oleh model bahasa AI.",
    statValue: "Sintaksis AI",
    statLabel: "Varians Panjang Kalimat & TTR",
    iconBg: "bg-amber-50",
    iconColor: "text-amber-600",
    accentBorder: "border-amber-100",
    badgeHex: "#EAB308",
    isSaved: false,
  },
  {
    tierId: "T4",
    category: "Komposit Agregasi",
    engine: "UU PDP & Sertifikasi",
    title: "Sertifikat QR & Audit",
    tags: ["UUID v4", "Interactive Heatmap", "PDF Resmi"],
    description: "Penggabungan skor terbobot dengan penerbitan sertifikat integritas akademik ber-QR code kriptografis yang valid publik.",
    statValue: "Formula 4-Tier",
    statLabel: "0.50 T1 + 0.35 T2 + 0.15 T3",
    iconBg: "bg-[#ededed]",
    iconColor: "text-audyr-ink",
    accentBorder: "border-[#ededed]",
    badgeHex: "#262626",
    isSaved: true,
  },
]);

function toggleSave(tier: TierCardItem) {
  tier.isSaved = !tier.isSaved;
}
</script>

<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8" aria-label="Tingkat Perlindungan Integritas Akademik">
    <!-- Header -->
    <div class="text-center max-w-2xl mx-auto space-y-3">
      <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
        <span>Arsitektur Deteksi 4-Tier</span>
      </div>
      <h2 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Empat Tingkat Perlindungan <span class="italic font-normal text-[#17191c]">Integritas Akademik</span>
      </h2>
      <p class="text-sm text-[#777b86] leading-relaxed font-normal">
        Dirancang untuk mendeteksi mulai dari salin-tempel <strong class="font-medium text-[#17191c]">verbatim langsung</strong> hingga parafrasa cerdas berbasis model bahasa besar (<strong class="italic font-medium text-[#17191c]">LLM</strong>).
      </p>
    </div>

    <!-- Steep Cards Grid (24px radius, pure paper, hairline borders) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="tier in tiers"
        :key="tier.tierId"
        class="bg-white rounded-[24px] p-6 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out flex flex-col justify-between group"
      >
        <div>
          <!-- Top Row: Circular Brand/Tier Icon + Save Pill Button -->
          <div class="flex items-center justify-between mb-4">
            <!-- Circular Icon Avatar with soft ring -->
            <div
              :class="[
                'w-10 h-10 rounded-full flex items-center justify-center border transition-transform duration-150 group-hover:scale-105',
                tier.iconBg,
                tier.accentBorder,
                tier.iconColor
              ]"
            >
              <!-- Tier 1 Hash Icon -->
              <svg v-if="tier.tierId === 'T1'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
              </svg>
              <!-- Tier 2 Vector/Brain Icon -->
              <svg v-else-if="tier.tierId === 'T2'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <!-- Tier 3 Feather/Syntax Icon -->
              <svg v-else-if="tier.tierId === 'T3'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <!-- Tier 4 Shield/Check Icon -->
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>

            <!-- Steep Pill Action Button -->
            <button
              type="button"
              class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-medium tracking-tight transition-colors duration-150 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]"
              :class="tier.isSaved ? 'bg-[#17191c] border-[#17191c] text-white' : 'bg-transparent border-[#ededed] text-[#17191c] hover:bg-[#f2f2f3]'"
              @click="toggleSave(tier)"
            >
              <span>{{ tier.isSaved ? 'Aktif' : 'Detail' }}</span>
              <svg class="w-3.5 h-3.5" :fill="tier.isSaved ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
          </div>

          <!-- Company/Category + Engine Subtitle -->
          <div class="flex items-center text-xs font-medium text-[#777b86]">
            <span>{{ tier.category }}</span>
            <span class="text-[#979799] font-normal ml-1.5 text-[11px] italic">{{ tier.engine }}</span>
          </div>

          <!-- Main Title -->
          <h3 class="text-base sm:text-lg font-semibold text-[#17191c] tracking-tight mt-0.5">
            {{ tier.title }}
          </h3>

          <!-- Tags in Steep pill containers -->
          <div class="flex flex-wrap gap-1.5 mt-3">
            <span
              v-for="tag in tier.tags"
              :key="tag"
              :class="[
                'px-2.5 py-0.5 rounded-full text-[11px] font-medium tracking-tight border',
                tier.tierId === 'T2' && tag === 'Bobot 35%'
                  ? 'bg-[#ecfdf5] border-[#a7f3d0] text-[#065f46]'
                  : 'bg-[#f2f2f3] border-[#ededed] text-[#17191c]'
              ]"
            >
              {{ tag }}
            </span>
          </div>

          <!-- Description paragraph -->
          <p class="text-xs text-[#777b86] leading-relaxed mt-3.5 font-normal">
            {{ tier.description }}
          </p>
        </div>

        <!-- Footer Row with Metric on Left and Black Pill Button on Right -->
        <div class="pt-4 mt-5 border-t border-[#ededed] flex items-center justify-between">
          <div>
            <div class="text-sm font-semibold text-[#17191c] tabular-nums">
              {{ tier.statValue }}
            </div>
            <div class="text-[10px] text-[#777b86] font-normal">
              {{ tier.statLabel }}
            </div>
          </div>

          <!-- Steep Dark Pill Action Button -->
          <router-link
            to="/dashboard"
            class="px-4 py-1.5 bg-[#17191c] hover:bg-[#2e3138] text-white text-xs font-medium rounded-full active:scale-[0.98] transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c]"
          >
            Uji Coba
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>
