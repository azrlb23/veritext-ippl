<script setup lang="ts">
// PipelineTiersGrid.vue - Modern Editorial Bento Architecture Grid
</script>

<template>
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 select-none" aria-label="Arsitektur Deteksi 4-Tier">
    <!-- Header -->
    <div class="text-center max-w-2xl mx-auto space-y-3 mb-10">
      <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
        <span>Arsitektur Deteksi 4-Tier</span>
      </div>
      <h2 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Tiga lapis kecerdasan untuk satu <span class="italic font-normal text-[#17191c]">kepastian integritas</span>
      </h2>
      <p class="text-sm text-[#777b86] leading-relaxed font-normal">
        Dirancang khusus untuk membedakan antara salin-tempel langsung, parafrasa cerdas berbasis sinonim, dan sintesis otomatis model bahasa AI.
      </p>
    </div>

    <!-- Bento Grid Container -->
    <div class="space-y-5">
      <!-- Row 1: Dual Large Cards (Hero Hybrid Comparison + Formula Gauge) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Card 1: Hybrid Lexical + Semantic Synergy (7 cols) -->
        <div class="lg:col-span-7 bg-white rounded-[24px] p-6 sm:p-8 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.06)] flex flex-col justify-between space-y-6">
          <div class="space-y-3">
            <div class="flex items-center space-x-2">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#fbe1d1] text-[#5d2a1a]">
                Sinergi Dua Mesin
              </span>
              <span class="text-xs text-[#777b86]">&bull;</span>
              <span class="text-xs text-[#777b86] font-mono">Tier 1 + Tier 2</span>
            </div>
            <h3 class="font-serif text-2xl font-normal text-[#17191c] tracking-tight">
              Mengapa satu algoritma saja tidak pernah cukup?
            </h3>
            <p class="text-xs sm:text-sm text-[#777b86] leading-relaxed font-normal">
              Pemeriksa plagiarisme konvensional hanya mengandalkan pencocokan teks langsung (*string matching*), sehingga mudah dikelabui oleh sinonim dan parafrasa. VeriText AI menggabungkan <strong class="font-medium text-[#17191c]">Winnowing hash</strong> berkecepatan tinggi dengan <strong class="font-medium text-[#17191c]">penalaran semantik dense 384D</strong> melalui pgvector.
            </p>
          </div>

          <!-- Micro Comparison Graphic -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <!-- Winnowing Box -->
            <div class="p-4 rounded-[16px] bg-[#fafafb] border border-[#ededed] space-y-1.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-[#17191c]">Winnowing Hashing</span>
                <span class="text-[10px] text-[#EF4444] font-medium font-mono">100% Identik</span>
              </div>
              <div class="h-1.5 bg-[#ededed] rounded-full overflow-hidden">
                <div class="h-full bg-[#EF4444] rounded-full w-full"></div>
              </div>
              <p class="text-[11px] text-[#777b86] leading-tight">
                Mendeteksi salin-tempel langsung kalimat demi kalimat tanpa distorsi.
              </p>
            </div>

            <!-- pgvector Box -->
            <div class="p-4 rounded-[16px] bg-[#fafafb] border border-[#ededed] space-y-1.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-[#17191c]">pgvector HNSW</span>
                <span class="text-[10px] text-[#F97316] font-medium font-mono">Semantik &ge; 0.75</span>
              </div>
              <div class="h-1.5 bg-[#ededed] rounded-full overflow-hidden">
                <div class="h-full bg-[#F97316] rounded-full w-[85%]"></div>
              </div>
              <p class="text-[11px] text-[#777b86] leading-tight">
                Menangkap parafrasa pintar dan sinonim dalam ruang vektor dense.
              </p>
            </div>
          </div>
        </div>

        <!-- Card 2: Composite Score Formula & Latency Gauge (5 cols) -->
        <div class="lg:col-span-5 bg-white rounded-[24px] p-6 sm:p-8 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.06)] flex flex-col justify-between space-y-6">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
                Formula Agregasi
              </span>
              <span class="text-[11px] text-[#059669] font-medium">&lt; 1.500 ms Latensi</span>
            </div>

            <div class="flex items-center justify-between gap-4">
              <div>
                <div class="text-[11px] text-[#777b86] font-medium">Formula Pembobotan Komposit</div>
                <div class="text-xl sm:text-2xl font-serif font-normal text-[#17191c] tracking-tight mt-0.5">
                  0.50 T1 + 0.35 T2 + 0.15 T3
                </div>
              </div>

              <!-- Circular Donut Gauge -->
              <div class="relative w-14 h-14 flex items-center justify-center flex-shrink-0">
                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    class="text-[#fbe1d1]"
                    stroke-width="3.5"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    stroke="#5d2a1a"
                    stroke-dasharray="100, 100"
                    stroke-linecap="round"
                    stroke-width="3.5"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div class="absolute flex flex-col items-center text-center">
                  <span class="text-[10px] font-bold text-[#17191c] leading-none">100%</span>
                  <span class="text-[6px] text-[#777b86] font-medium">Valid</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Weight Distribution Bars -->
          <div class="space-y-2 pt-2 border-t border-[#ededed] text-xs">
            <div class="flex items-center justify-between">
              <span class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-[#EF4444]"></span>
                <span class="text-[#777b86]">Tier 1: Hashing Leksikal</span>
              </span>
              <span class="font-mono font-medium text-[#17191c]">50%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-[#F97316]"></span>
                <span class="text-[#777b86]">Tier 2: Parafrasa Semantik</span>
              </span>
              <span class="font-mono font-medium text-[#17191c]">35%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-[#EAB308]"></span>
                <span class="text-[#777b86]">Tier 3: Stilometri AI</span>
              </span>
              <span class="font-mono font-medium text-[#17191c]">15%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 2: Three Clean Engine Cards (3 cols) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <!-- Tier 1 Card -->
        <div class="bg-white rounded-[24px] p-6 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_15px_30px_-10px_rgba(0,0,0,0.05)] hover:border-[#17191c] transition-all duration-150 ease-out space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#EF4444] px-2.5 py-0.5 rounded-full bg-red-50 border border-red-100">
              Tier 1 &bull; Leksikal
            </span>
            <span class="text-xs font-mono font-medium text-[#777b86]">k=5, w=4</span>
          </div>

          <div class="space-y-1.5">
            <h4 class="font-serif text-lg font-normal text-[#17191c] tracking-tight">
              Winnowing Fingerprinting
            </h4>
            <p class="text-xs text-[#777b86] leading-relaxed font-normal">
              Algoritma Rabin-Karp 64-bit membentuk jendela geser (*sliding window*) untuk mendeteksi penjiplakan salin-tempel langsung dengan efisiensi memori optimal.
            </p>
          </div>

          <div class="pt-3 border-t border-[#ededed] flex items-center justify-between text-[11px]">
            <span class="text-[#777b86]">Kompleksitas: <strong class="text-[#17191c] font-mono font-normal">O(n)</strong></span>
            <span class="font-medium text-[#17191c]">Latensi &lt; 10 ms</span>
          </div>
        </div>

        <!-- Tier 2 Card -->
        <div class="bg-white rounded-[24px] p-6 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_15px_30px_-10px_rgba(0,0,0,0.05)] hover:border-[#17191c] transition-all duration-150 ease-out space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#F97316] px-2.5 py-0.5 rounded-full bg-orange-50 border border-orange-100">
              Tier 2 &bull; Semantik
            </span>
            <span class="text-xs font-mono font-medium text-[#777b86]">384 Dimensi</span>
          </div>

          <div class="space-y-1.5">
            <h4 class="font-serif text-lg font-normal text-[#17191c] tracking-tight">
              pgvector HNSW Cosine
            </h4>
            <p class="text-xs text-[#777b86] leading-relaxed font-normal">
              Memproyeksikan makna naskah ke ruang vektor dense (*MiniLM-L12-v2*) untuk mengungkap parafrasa cerdas dan restrukturisasi kalimat pasif-aktif.
            </p>
          </div>

          <div class="pt-3 border-t border-[#ededed] flex items-center justify-between text-[11px]">
            <span class="text-[#777b86]">Indeks Vektor: <strong class="text-[#17191c] font-mono font-normal">HNSW (m=16)</strong></span>
            <span class="font-medium text-[#17191c]">Sim &ge; 0.75</span>
          </div>
        </div>

        <!-- Tier 3 Card -->
        <div class="bg-white rounded-[24px] p-6 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_15px_30px_-10px_rgba(0,0,0,0.05)] hover:border-[#17191c] transition-all duration-150 ease-out space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#b45309] px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-100">
              Tier 3 &bull; Stilometri
            </span>
            <span class="text-xs font-mono font-medium text-[#777b86]">Burstiness</span>
          </div>

          <div class="space-y-1.5">
            <h4 class="font-serif text-lg font-normal text-[#17191c] tracking-tight">
              Pola Sintaksis Model LLM
            </h4>
            <p class="text-xs text-[#777b86] leading-relaxed font-normal">
              Mengevaluasi varians panjang kalimat dan kekayaan leksikal (*Type-Token Ratio*) untuk membedakan ritme tulisan manusia asli dengan teks robotik AI.
            </p>
          </div>

          <div class="pt-3 border-t border-[#ededed] flex items-center justify-between text-[11px]">
            <span class="text-[#777b86]">Metrik: <strong class="text-[#17191c] font-mono font-normal">TTR &amp; Varians</strong></span>
            <span class="font-medium text-[#17191c]">Anomali &lt; 0.20</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
