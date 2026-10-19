<script setup lang="ts">
// InvertedDarkSection.vue - Full Implementation of Steep Reference Image 2:
// 1. Light Academic Trust & Institutional Stories Band (Top of Image 2)
// 2. High-Contrast Inverted Ink-Black Section (Bottom of Image 2)
</script>

<template>
  <div class="space-y-0 select-none">
    <!-- ============================================================ -->
    <!-- PART 1: Light Academic Trust & Stories Band (Top of Image 2) -->
    <!-- ============================================================ -->
    <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-[#ededed]/80">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        <!-- Left Column: Story teaser & Institutional Logos -->
        <div class="lg:col-span-7 space-y-6">
          <div class="space-y-2">
            <span class="text-xs font-semibold uppercase tracking-wider text-[#777b86]">
              Mengapa Institusi Memilih VeriText
            </span>
            <h3 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight">
              Integritas karya ilmiah tanpa kompromi privasi data.
            </h3>
          </div>

          <!-- Action Links Pill -->
          <div class="flex items-center space-x-4 pt-1">
            <router-link
              to="/verify"
              class="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full bg-[#17191c] hover:bg-[#2b2e34] text-white text-xs font-medium active:scale-[0.98] transition-colors"
            >
              <span>Verifikasi Sertifikat QR</span>
              <span>&rarr;</span>
            </router-link>
            <router-link
              to="/corpus"
              class="text-xs font-medium text-[#777b86] hover:text-[#17191c] transition-colors"
            >
              Bank Korpus Riset &rarr;
            </router-link>
          </div>

          <!-- Monochrome Academic Standards Logo Line -->
          <div class="pt-6 border-t border-[#ededed]">
            <div class="text-[10px] font-mono uppercase tracking-wider text-[#979799] mb-3">
              Kepatuhan &amp; Akreditasi Nasional
            </div>
            <div class="flex flex-wrap items-center gap-6 sm:gap-8 text-sm sm:text-base font-semibold text-[#17191c]/70 tracking-tighter">
              <span class="hover:text-[#17191c] transition-colors">UU PDP 27/2022</span>
              <span class="hover:text-[#17191c] transition-colors">SINTA KEMDIKBUD</span>
              <span class="hover:text-[#17191c] transition-colors">PERPUSNAS</span>
              <span class="hover:text-[#17191c] transition-colors">TELKOM UNIV</span>
            </div>
          </div>
        </div>

        <!-- Right Column: Visual Photo Card with 24px radius (like Image 2 right) -->
        <div class="lg:col-span-5">
          <div class="relative rounded-[24px] overflow-hidden border border-[#ededed] bg-[#fafafb] p-6 shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-[#fbe1d1] text-[#5d2a1a]">
                Studi Kasus 2026
              </span>
              <span class="text-[11px] text-[#777b86] font-mono">Institut Riset</span>
            </div>
            <p class="text-xs text-[#515151] leading-relaxed">
              "VeriText AI menghemat 85% waktu penelaahan dokumen skripsi kami. Pemeriksaan leksikal dan semantik dilakukan dalam 1,2 detik dengan jaminan hak privasi mahasiswa sesuai UU PDP."
            </p>
            <div class="flex items-center space-x-3 pt-2 border-t border-[#ededed]">
              <div class="w-7 h-7 rounded-full bg-[#17191c] text-white flex items-center justify-center font-bold text-xs">
                Dr
              </div>
              <div class="text-[11px] leading-tight">
                <div class="font-semibold text-[#17191c]">Dr. Budi Santoso, M.Kom.</div>
                <div class="text-[#777b86]">Ketua Komite Integritas Akademik</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================ -->
    <!-- PART 2: Inverted Ink-Black Editorial Section (Bottom Image 2) -->
    <!-- ============================================================ -->
    <section class="relative bg-[#17191c] text-white py-24 sm:py-32 overflow-hidden">
      <!-- Subtle Ambient Radial Glow in the dark surface -->
      <div
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 w-full max-w-5xl h-[500px] bg-[radial-gradient(ellipse_60%_50%_at_50%_50%,rgba(251,225,209,0.08),rgba(0,0,0,0))] blur-3xl pointer-events-none"
        aria-hidden="true"
      ></div>

      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8 relative z-10">
        <!-- Eyebrow Pill Label -->
        <div class="inline-flex items-center space-x-1.5 px-3.5 py-1 rounded-full bg-white/10 hover:bg-white/15 text-white/90 text-xs font-medium border border-white/15 backdrop-blur transition-colors">
          <span>Engine Hybrid 4-Tier</span>
          <span class="text-[#a3a6af] font-mono">&gt;</span>
        </div>

        <!-- Headline Serif (Signifier regular 400 with italic emphasis) -->
        <h2 class="font-serif text-4xl sm:text-6xl lg:text-[68px] font-normal text-white tracking-[-0.03em] leading-[1.14] max-w-4xl mx-auto">
          Deteksi esensi, bukan <span class="italic font-normal">sekadar kata</span>
        </h2>

        <!-- Subtitle -->
        <p class="text-base sm:text-xl text-[#a3a6af] max-w-2xl mx-auto leading-relaxed font-normal tracking-tight">
          Model pembanding semantik dense 384-dimensi dan winnowing hash kriptografis untuk integritas karya ilmiah tanpa kompromi.
        </p>

        <!-- Frosted Pill CTA Button -->
        <div class="pt-2">
          <router-link
            to="/dashboard"
            class="inline-flex items-center justify-center px-7 py-3 rounded-full bg-white/10 hover:bg-white/20 text-white font-medium text-sm tracking-tight border border-white/20 backdrop-blur active:scale-[0.98] transition-all duration-150 ease-out shadow-lg space-x-2"
          >
            <span>Buka Workspace Audit</span>
            <span class="text-white/80">&rarr;</span>
          </router-link>
        </div>

        <!-- Academic Trust & Compliance Band (Monochromatic) -->
        <div class="pt-16 sm:pt-20 border-t border-white/10 mt-16 max-w-5xl mx-auto">
          <div class="text-[11px] font-semibold text-[#a3a6af] uppercase tracking-wider mb-6">
            Standar Kepatuhan Akademik &amp; Kriptografi Institusional
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-left">
            <!-- Item 1: UU PDP -->
            <div class="p-4 rounded-[16px] bg-white/[0.03] border border-white/10 space-y-1">
              <div class="text-xs font-mono font-semibold text-white">UU PDP No. 27/2022</div>
              <div class="text-[11px] text-[#a3a6af] leading-tight">Perlindungan privasi naskah tanpa pelatihan model pihak ketiga</div>
            </div>

            <!-- Item 2: SHA-256 -->
            <div class="p-4 rounded-[16px] bg-white/[0.03] border border-white/10 space-y-1">
              <div class="text-xs font-mono font-semibold text-white">SHA-256 Hash</div>
              <div class="text-[11px] text-[#a3a6af] leading-tight">Stempel kriptografis bukti keaslian sertifikat publik QR</div>
            </div>

            <!-- Item 3: pgvector -->
            <div class="p-4 rounded-[16px] bg-white/[0.03] border border-white/10 space-y-1">
              <div class="text-xs font-mono font-semibold text-white">pgvector HNSW</div>
              <div class="text-[11px] text-[#a3a6af] leading-tight">Indeks dense 384-dimensi untuk penalaran semantik kosinus</div>
            </div>

            <!-- Item 4: Celery Queue -->
            <div class="p-4 rounded-[16px] bg-white/[0.03] border border-white/10 space-y-1">
              <div class="text-xs font-mono font-semibold text-white">Celery &amp; Redis</div>
              <div class="text-[11px] text-[#a3a6af] leading-tight">Antrean asynchronous terdistribusi dengan throughput tinggi</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
