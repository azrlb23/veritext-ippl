<script setup lang="ts">
// DashboardShowcaseWindow.vue - Replicating Steep macOS Application Window Showcase (Image 1 & 3 Reference)
</script>

<template>
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 select-none" aria-label="Pratinjau Live Workspace">
    <!-- Section Introduction Header -->
    <div class="text-center max-w-2xl mx-auto space-y-3 mb-10">
      <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#fafafb] text-[#17191c] border border-[#ededed]">
        <span>Live Product Canvas</span>
      </div>
      <h2 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Satu Kanvas Terpadu untuk <span class="italic font-normal text-[#17191c]">Seluruh Analisis</span>
      </h2>
      <p class="text-sm text-[#777b86] leading-relaxed font-normal">
        Semua artefak yang Anda lihat di beranda bermuara dalam ruang kerja interaktif — memadukan deteksi leksikal, vektor semantik, dan narasi diagnosis AI.
      </p>
    </div>

    <!-- macOS Application Window Shell -->
    <div class="bg-white rounded-[24px] sm:rounded-[28px] border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_30px_60px_-15px_rgba(0,0,0,0.12)] overflow-hidden">
      <!-- Titlebar / Header Window macOS -->
      <div class="h-12 bg-[#fafafb] border-b border-[#ededed] px-4 sm:px-6 flex items-center justify-between">
        <!-- Traffic Light Dots -->
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded-full bg-[#ff5f56] border border-[#e0443e]/40 inline-block"></span>
          <span class="w-3 h-3 rounded-full bg-[#ffbd2e] border border-[#dea123]/40 inline-block"></span>
          <span class="w-3 h-3 rounded-full bg-[#27c93f] border border-[#1aab29]/40 inline-block"></span>
        </div>

        <!-- Breadcrumb & Workspace Title -->
        <div class="flex items-center space-x-2 text-xs font-medium text-[#777b86]">
          <span class="text-[#17191c] font-semibold">VeriText Academic</span>
          <span>/</span>
          <span>Workspace Audit</span>
          <span>/</span>
          <span class="text-[#17191c]">Naskah-Skripsi-2026.pdf</span>
        </div>

        <!-- Action / Status Pill -->
        <div class="flex items-center space-x-2">
          <span class="hidden sm:inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
            Audit Selesai
          </span>
          <router-link
            to="/dashboard"
            class="text-[11px] font-medium text-[#17191c] hover:bg-[#f2f2f3] px-3 py-1 rounded-full border border-[#ededed] transition-colors"
          >
            Buka Workspace &rarr;
          </router-link>
        </div>
      </div>

      <!-- Window Body: Sidebar + Main Content Area -->
      <div class="flex flex-col md:flex-row min-h-[620px]">
        <!-- Left Sidebar (Mist Gray #fafafb) -->
        <div class="w-full md:w-64 bg-[#fafafb] border-r border-[#ededed] p-4 flex flex-col justify-between hidden md:flex text-xs space-y-6">
          <div class="space-y-5">
            <!-- Workspace Switcher Chip -->
            <div class="flex items-center justify-between p-2 rounded-[14px] bg-white border border-[#ededed] shadow-sm">
              <div class="flex items-center space-x-2.5">
                <div class="w-6 h-6 rounded-full bg-[#17191c] text-white flex items-center justify-center font-bold text-[10px]">
                  V
                </div>
                <div class="leading-tight">
                  <div class="font-semibold text-[#17191c] text-xs">Laboratorium AI</div>
                  <div class="text-[10px] text-[#777b86]">Fakultas Teknik</div>
                </div>
              </div>
              <svg class="w-3.5 h-3.5 text-[#777b86]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>

            <!-- Primary Navigation Links -->
            <div class="space-y-1">
              <div class="text-[10px] font-bold text-[#979799] uppercase tracking-wider px-2 py-1">Menu Utama</div>
              <a href="#" class="flex items-center space-x-2.5 px-2.5 py-1.5 rounded-full bg-[#17191c] text-white font-medium">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span>Ringkasan Audit</span>
              </a>
              <a href="#" class="flex items-center space-x-2.5 px-2.5 py-1.5 rounded-full text-[#777b86] hover:text-[#17191c] hover:bg-white transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Heatmap Interaktif</span>
              </a>
              <a href="#" class="flex items-center space-x-2.5 px-2.5 py-1.5 rounded-full text-[#777b86] hover:text-[#17191c] hover:bg-white transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span>Repositori Korpus</span>
              </a>
              <a href="#" class="flex items-center space-x-2.5 px-2.5 py-1.5 rounded-full text-[#777b86] hover:text-[#17191c] hover:bg-white transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Metrik pgvector HNSW</span>
              </a>
            </div>

            <!-- Teams / Departemen Section -->
            <div class="space-y-1">
              <div class="text-[10px] font-bold text-[#979799] uppercase tracking-wider px-2 py-1">Program Studi</div>
              <div class="flex items-center space-x-2 px-2.5 py-1 text-xs text-[#777b86]">
                <span class="w-2 h-2 rounded-full bg-[#fbe1d1] border border-[#5d2a1a]/30"></span>
                <span>Teknik Informatika</span>
              </div>
              <div class="flex items-center space-x-2 px-2.5 py-1 text-xs text-[#777b86]">
                <span class="w-2 h-2 rounded-full bg-[#ecfdf5] border border-[#065f46]/30"></span>
                <span>Sains Data</span>
              </div>
              <div class="flex items-center space-x-2 px-2.5 py-1 text-xs text-[#777b86]">
                <span class="w-2 h-2 rounded-full bg-[#f2f2f3] border border-[#17191c]/30"></span>
                <span>Sistem Informasi</span>
              </div>
            </div>
          </div>

          <!-- Bottom Privacy Note -->
          <div class="p-3 rounded-[16px] bg-white border border-[#ededed] space-y-1">
            <div class="flex items-center justify-between text-[10px]">
              <span class="font-bold text-[#17191c]">UU PDP No. 27/2022</span>
              <span class="text-[#059669] font-semibold">Tersertifikasi</span>
            </div>
            <p class="text-[10px] text-[#777b86] leading-tight">
              Enkripsi SHA-256 melindungi hak cipta naskah mahasiswa secara penuh.
            </p>
          </div>
        </div>

        <!-- Main Content Canvas (White Background) -->
        <div class="flex-1 p-5 sm:p-7 space-y-6 bg-white overflow-hidden">
          <!-- Greeting & Narrative Subheader -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#ededed] pb-4">
            <div>
              <h3 class="font-serif text-2xl font-normal text-[#17191c] tracking-tight">
                Laporan Diagnostik Naskah
              </h3>
              <p class="text-xs text-[#777b86] mt-0.5">
                Pengujian naskah ilmiah berbasis korpus nasional &bull; Waktu proses: <span class="text-[#17191c] font-medium">1.120 ms</span>
              </p>
            </div>
            <div class="flex items-center space-x-2 self-start sm:self-auto">
              <span class="text-xs text-[#777b86] tabular-nums">UUID: <strong class="font-mono text-[#17191c]">f47ac10b</strong></span>
              <button type="button" class="px-3 py-1 rounded-full bg-[#17191c] text-white text-xs font-medium">
                Unduh PDF
              </button>
            </div>
          </div>

          <!-- Floating AI Prompt Callout (Image 1 Signature Element) -->
          <div class="relative bg-white rounded-[20px] p-4 sm:p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_12px_24px_-8px_rgba(0,0,0,0.08)] flex items-start sm:items-center justify-between gap-4">
            <div class="space-y-1">
              <div class="inline-flex items-center space-x-1.5 text-[10px] font-bold text-[#5d2a1a] uppercase tracking-wider bg-[#fbe1d1] px-2.5 py-0.5 rounded-full">
                <span>Pertanyaan Analisis AI</span>
              </div>
              <p class="text-sm sm:text-base font-normal text-[#17191c] tracking-tight">
                "Bagaimana tingkat orisinalitas naskah dan distribusi parafrasa semantik pada bab metodologi riset?"
              </p>
            </div>
            <div class="w-8 h-8 rounded-full bg-[#17191c] text-white flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>

          <!-- Three Connected Metric Artifacts Grid (Sama dengan Hero) -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Artifact 1: Winnowing N-Gram Leksikal -->
            <div class="p-4 rounded-[20px] border border-[#ededed] bg-[#fafafb] space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-lg font-bold text-[#17191c] tabular-nums">3 503</div>
                  <div class="text-[10px] text-[#777b86]">Token Sidik Jari Leksikal</div>
                </div>
                <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white border border-[#ededed] text-[#17191c]">
                  k=5, w=4
                </span>
              </div>
              <!-- Mini Histogram -->
              <div class="flex items-end space-x-1 h-8 pt-1">
                <span class="w-2 bg-[#17191c]/25 rounded-t-sm h-[40%]"></span>
                <span class="w-2 bg-[#17191c]/45 rounded-t-sm h-[70%]"></span>
                <span class="w-2 bg-[#17191c]/70 rounded-t-sm h-[90%]"></span>
                <span class="w-2 bg-[#17191c]/50 rounded-t-sm h-[60%]"></span>
                <span class="w-2 bg-[#17191c] rounded-t-sm h-[100%]"></span>
              </div>
              <div class="text-[10px] text-[#777b86] flex justify-between border-t border-[#ededed] pt-2">
                <span>Rujukan Terdekat</span>
                <span class="text-[#17191c] font-medium">Skripsi IF-2023</span>
              </div>
            </div>

            <!-- Artifact 2: Target Integritas 75% Circular Ring Gauge -->
            <div class="p-4 rounded-[20px] border border-[#ededed] bg-[#fafafb] flex items-center justify-between gap-3">
              <div class="space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-[#5d2a1a]">Skor Orisinalitas</div>
                <div class="text-2xl font-bold text-[#17191c] tabular-nums">84.8%</div>
                <div class="text-[10px] text-[#059669] font-medium">Batas Aman (&lt; 20% Kesamaan)</div>
              </div>
              <!-- Donut Gauge 75% of target style -->
              <div class="relative w-16 h-16 flex items-center justify-center flex-shrink-0">
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
                    stroke-dasharray="85, 100"
                    stroke-linecap="round"
                    stroke-width="3.5"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div class="absolute flex flex-col items-center text-center">
                  <span class="text-xs font-bold text-[#17191c] tabular-nums leading-none">85%</span>
                  <span class="text-[7px] text-[#777b86] font-medium">Murni</span>
                </div>
              </div>
            </div>

            <!-- Artifact 3: Kurva Parafrasa Semantik dense 384D -->
            <div class="p-4 rounded-[20px] border border-[#ededed] bg-[#fafafb] space-y-2">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-lg font-bold text-[#17191c] tabular-nums">46.2%</div>
                  <div class="text-[10px] text-[#777b86]">Penelusuran Parafrasa Semantik</div>
                </div>
                <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[#065f46]">
                  HNSW
                </span>
              </div>
              <!-- Sparkline -->
              <svg class="w-full h-8 overflow-visible" viewBox="0 0 100 28" fill="none">
                <line x1="0" y1="16" x2="100" y2="16" stroke="#ededed" stroke-width="1" stroke-dasharray="2,2" />
                <path d="M 5 22 Q 25 20, 45 13 T 75 12 T 95 5" stroke="#17191c" stroke-width="1.75" stroke-linecap="round" fill="none" />
                <circle cx="95" cy="5" r="2.5" fill="#17191c" />
              </svg>
              <div class="text-[10px] text-[#777b86] flex justify-between border-t border-[#ededed] pt-1.5 font-mono">
                <span>Bab I</span><span>Bab II</span><span>Bab III</span><span class="text-[#17191c] font-bold">Bab IV</span>
              </div>
            </div>
          </div>

          <!-- Editorial Narrative Findings ("Key Findings" - Steep Signature Image 1) -->
          <div class="p-5 rounded-[20px] bg-[#fafafb] border border-[#ededed] space-y-4 text-xs">
            <!-- High-Level Impact -->
            <div>
              <div class="text-[11px] font-bold text-[#17191c] uppercase tracking-wider mb-1">
                Kesimpulan Integritas Tingkat Tinggi (High-Level Impact)
              </div>
              <p class="text-[#515151] leading-relaxed">
                Skor orisinalitas naskah mencapai <strong class="font-semibold text-[#17191c]">84.8%</strong>. Tingkat kesamaan komposit terdeteksi sebesar <strong class="font-semibold text-[#17191c]">15.2%</strong> (10.5% leksikal Tier 1, 3.8% parafrasa Tier 2, dan 0.9% anomali gaya tulisan). Naskah dinyatakan <strong class="text-[#059669] font-semibold">Layak Maju ke Sidang Ujian</strong> karena masih di bawah batas toleransi maksimal 20%.
              </p>
            </div>

            <!-- Bulleted Key Findings -->
            <div class="space-y-2 border-t border-[#ededed] pt-3">
              <div class="text-[11px] font-bold text-[#17191c] uppercase tracking-wider">
                Temuan Kunci Hasil Komparasi (Key Findings)
              </div>
              <ul class="space-y-2 text-[#515151]">
                <li class="flex items-start space-x-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#EF4444] mt-1.5 flex-shrink-0"></span>
                  <span>
                    <strong class="font-medium text-[#17191c]">Kecocokan Leksikal Langsung:</strong> Ditemukan 12 penggalan kalimat verbatim yang identik dengan repositori skripsi internal 2023 pada paragraf definisi landasan teori.
                  </span>
                </li>
                <li class="flex items-start space-x-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#F97316] mt-1.5 flex-shrink-0"></span>
                  <span>
                    <strong class="font-medium text-[#17191c]">Parafrasa Semantik Cerdas:</strong> Algoritma pgvector mendeteksi 4 kalimat dengan susunan kalimat diubah dan sinonim digunakan, namun jarak kosinus semantik tetap sangat dekat (&ge; 0.82).
                  </span>
                </li>
                <li class="flex items-start space-x-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#EAB308] mt-1.5 flex-shrink-0"></span>
                  <span>
                    <strong class="font-medium text-[#17191c]">Pola Gaya Bahasa Manusia:</strong> Analisis varians panjang kalimat (<em class="italic">Burstiness</em> = 0.42) dan kekayaan kosakata (<em class="italic">TTR</em> = 0.68) memastikan draf ditulis oleh manusia secara autentik.
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
