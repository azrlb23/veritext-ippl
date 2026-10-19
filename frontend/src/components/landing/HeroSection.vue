<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-7 pt-6 sm:pt-10">
    <!-- Top Pill Badge (Steep Blush Peach Accent) -->
    <div class="inline-flex items-center px-4 py-1.5 rounded-full bg-[#fbe1d1] border border-[#f5cdb6] text-[#5d2a1a] text-xs font-medium tracking-tight shadow-sm">
      <span class="text-[12px] tracking-wide">
        Arsitektur <strong class="italic font-semibold">Hybrid Lexical &amp; Semantic AI Engine</strong> (SDD 3.6.2)
      </span>
    </div>

    <!-- Steep Editorial Display Headline (Serif weight 400 with italic phrase) -->
    <h1 class="font-serif text-4xl sm:text-6xl lg:text-[64px] font-normal text-[#17191c] tracking-[-0.025em] max-w-4xl mx-auto leading-[1.18]">
      Presisi Deteksi Plagiarisme Cerdas Melalui <span class="italic text-[#17191c]">Pipa Hybrid 4-Tier</span>
    </h1>

    <!-- Editorial Subheading (Sohne 17px Slate Gray) -->
    <p class="text-base sm:text-[18px] text-[#777b86] max-w-2xl mx-auto leading-[1.5] tracking-tight font-normal">
      VeriText AI mengombinasikan algoritma sidik jari leksikal <strong class="font-medium text-[#17191c]">Winnowing</strong>, inferensi semantik <strong class="font-medium text-[#17191c]">pgvector HNSW</strong>, dan verifikasi <strong class="italic font-medium text-[#17191c]">stilometri AI</strong> untuk menjaga integritas karya akademik bebas manipulasi.
    </p>

    <!-- Steep Two-Button Pill Row: Filled Primary (Ink #17191c, 9999px) + Ghost Secondary -->
    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
      <router-link
        to="/dashboard"
        class="inline-flex items-center justify-center px-6 py-3 rounded-full bg-[#17191c] hover:bg-[#2b2e34] text-white font-medium text-sm tracking-tight active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c] focus-visible:ring-offset-2 transition-all duration-150 ease-out"
      >
        <span>Mulai Uji Naskah Sekarang</span>
        <span class="ml-2" aria-hidden="true">&rarr;</span>
      </router-link>
      <router-link
        to="/corpus"
        class="inline-flex items-center justify-center px-6 py-3 rounded-full bg-transparent border border-[#17191c] hover:bg-[#fafafb] text-[#17191c] font-medium text-sm tracking-tight active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#17191c] focus-visible:ring-offset-2 transition-all duration-150 ease-out"
      >
        Jelajahi Bank Korpus
      </router-link>
    </div>

    <!-- Microcopy Below Buttons -->
    <p class="text-xs text-[#979799] tracking-tight font-normal">
      Kepatuhan <strong class="italic font-medium text-[#777b86]">UU PDP No. 27/2022</strong> &bull; Enkripsi SHA-256 Naskah &bull; Tanpa Penyimpanan Teks Mentah Tanpa Izin
    </p>

    <!-- Steep Floating Product Artifacts (20px radius, hairline border, subtle elevation) -->
    <div class="pt-10 border-t border-[#ededed] max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4 text-left">
      <div class="p-5 rounded-[20px] bg-white border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 rounded-full bg-[#fef2f2] border border-[#fee2e2] flex items-center justify-center text-[#dc2626]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
            </svg>
          </div>
          <span class="px-2.5 py-0.5 rounded-full bg-[#f2f2f3] text-[10px] text-[#17191c] font-medium">Tier 1</span>
        </div>
        <div class="text-[11px] font-medium text-[#979799] uppercase tracking-wider">Algoritma Leksikal</div>
        <div class="mt-0.5 text-sm font-semibold text-[#17191c] tabular-nums">Winnowing (k=5, w=4)</div>
        <div class="text-[11px] text-[#737373] mt-1 font-normal">Hash Rabin-Karp 64-bit</div>
      </div>

      <div class="p-5 rounded-[20px] bg-white border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 rounded-full bg-[#fff7ed] border border-[#ffedd5] flex items-center justify-center text-[#ea580c]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="px-2.5 py-0.5 rounded-full bg-[#f2f2f3] text-[10px] text-[#17191c] font-medium">Tier 2</span>
        </div>
        <div class="text-[11px] font-medium text-[#979799] uppercase tracking-wider">Indeks Semantik</div>
        <div class="mt-0.5 text-sm font-semibold text-[#17191c] tabular-nums">384-d pgvector HNSW</div>
        <div class="text-[11px] text-[#737373] mt-1 font-normal">MiniLM-L12-v2 Cosine</div>
      </div>

      <div class="p-5 rounded-[20px] bg-white border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 rounded-full bg-[#ecfdf5] border border-[#a7f3d0] flex items-center justify-center text-[#065f46]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span class="px-2.5 py-0.5 rounded-full bg-[#ecfdf5] text-[10px] text-[#065f46] font-medium border border-[#a7f3d0]">UU PDP</span>
        </div>
        <div class="text-[11px] font-medium text-[#979799] uppercase tracking-wider">Kepatuhan Privasi</div>
        <div class="mt-0.5 text-sm font-semibold text-[#17191c] tabular-nums">UU PDP No. 27/2022</div>
        <div class="text-[11px] text-[#737373] mt-1 font-normal">Enkripsi SHA-256 Naskah</div>
      </div>

      <div class="p-5 rounded-[20px] bg-white border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] hover:border-[#17191c] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 rounded-full bg-[#f2f2f3] border border-[#ededed] flex items-center justify-center text-[#17191c]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span class="px-2.5 py-0.5 rounded-full bg-[#f2f2f3] text-[10px] text-[#17191c] font-medium border border-[#ededed]">Fast</span>
        </div>
        <div class="text-[11px] font-medium text-[#979799] uppercase tracking-wider">Target Latensi</div>
        <div class="mt-0.5 text-sm font-semibold text-[#17191c] tabular-nums">&lt; 1.500 ms</div>
        <div class="text-[11px] text-[#737373] mt-1 font-normal">Inferensi &amp; Query DB</div>
      </div>
    </div>
  </section>
</template>
