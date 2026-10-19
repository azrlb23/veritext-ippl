<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6 pt-4 sm:pt-8">
    <!-- Top Pill Badge (Mint Whisper) -->
    <div class="inline-flex items-center px-3.5 py-1 rounded-full bg-[#ecfdf5] border border-[#a7f3d0] text-[#065f46] text-xs font-semibold tracking-tight shadow-sm">
      <span class="text-[11px] uppercase tracking-wide">
        Arsitektur <strong class="italic font-bold">Hybrid Lexical &amp; Semantic AI Engine</strong> (SDD 3.6.2)
      </span>
    </div>

    <!-- Editorial Monograph Headline with Extra Bold & Italic Bold Variant -->
    <h1 class="text-3xl sm:text-5xl lg:text-[52px] font-extrabold text-[#262626] tracking-tight max-w-4xl mx-auto leading-[1.12]">
      Presisi Deteksi Plagiarisme Cerdas Melalui <span class="italic font-bold text-[#262626] underline decoration-[#ededed] decoration-4 underline-offset-8">Pipa Hybrid 4-Tier</span>
    </h1>

    <!-- Editorial Subheading -->
    <p class="text-base sm:text-lg text-[#686868] max-w-2xl mx-auto leading-[1.63] tracking-tight font-normal">
      VeriText AI mengombinasikan algoritma sidik jari leksikal <strong class="font-bold text-[#262626]">Winnowing</strong>, inferensi semantik <strong class="font-bold text-[#262626]">pgvector HNSW</strong>, dan verifikasi <strong class="italic font-bold text-[#262626]">stilometri AI</strong> untuk menjaga integritas karya akademik bebas manipulasi.
    </p>

    <!-- Two-Button Row: Filled Primary (Ink #262626, 4px radius) + Ghost Secondary -->
    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
      <router-link
        to="/dashboard"
        class="inline-flex items-center justify-center px-6 py-2.5 rounded-[4px] bg-[#262626] hover:bg-[#171717] text-white font-bold text-sm tracking-tight shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)] active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] focus-visible:ring-offset-2 transition-all duration-150 ease-out"
      >
        <span>Mulai Uji Naskah Sekarang</span>
        <span class="ml-2 font-bold" aria-hidden="true">&rarr;</span>
      </router-link>
      <router-link
        to="/corpus"
        class="inline-flex items-center justify-center px-6 py-2.5 rounded-[4px] bg-transparent border border-[#ededed] hover:bg-[#fafafa] hover:border-[#d4d4d4] text-[#262626] font-semibold text-sm tracking-tight active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] focus-visible:ring-offset-2 transition-all duration-150 ease-out"
      >
        Jelajahi Bank Korpus
      </router-link>
    </div>

    <!-- Microcopy Below Buttons -->
    <p class="text-xs text-[#737373] tracking-tight">
      Kepatuhan <strong class="italic font-bold text-[#515151]">UU PDP No. 27/2022</strong> &bull; Enkripsi SHA-256 Naskah &bull; Tanpa Penyimpanan Teks Mentah Tanpa Izin
    </p>

    <!-- Utilitarian Academic Trust & Spec Matrix in Audyr 14px Card Style -->
    <div class="pt-10 border-t border-[#ededed] max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4 text-left">
      <div class="p-4 rounded-[14px] bg-white border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] hover:border-[#d4d4d4] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-2">
          <div class="w-8 h-8 rounded-full bg-[#fef2f2] border border-[#fee2e2] flex items-center justify-center text-[#dc2626]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
            </svg>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-[#ededed] text-[10px] text-[#262626] font-bold">Tier 1</span>
        </div>
        <div class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">Algoritma Leksikal</div>
        <div class="mt-0.5 text-sm font-extrabold text-[#262626] tabular-nums">Winnowing (k=5, w=4)</div>
        <div class="text-[11px] text-[#737373] mt-1 font-medium">Hash Rabin-Karp 64-bit</div>
      </div>

      <div class="p-4 rounded-[14px] bg-white border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] hover:border-[#d4d4d4] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-2">
          <div class="w-8 h-8 rounded-full bg-[#fff7ed] border border-[#ffedd5] flex items-center justify-center text-[#ea580c]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-[#ededed] text-[10px] text-[#262626] font-bold">Tier 2</span>
        </div>
        <div class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">Indeks Semantik</div>
        <div class="mt-0.5 text-sm font-extrabold text-[#262626] tabular-nums">384-d pgvector HNSW</div>
        <div class="text-[11px] text-[#737373] mt-1 font-medium">MiniLM-L12-v2 Cosine</div>
      </div>

      <div class="p-4 rounded-[14px] bg-white border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] hover:border-[#d4d4d4] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-2">
          <div class="w-8 h-8 rounded-full bg-[#ecfdf5] border border-[#a7f3d0] flex items-center justify-center text-[#065f46]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-[#ecfdf5] text-[10px] text-[#065f46] font-bold border border-[#a7f3d0]">UU PDP</span>
        </div>
        <div class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">Kepatuhan Privasi</div>
        <div class="mt-0.5 text-sm font-extrabold text-[#262626] tabular-nums">UU PDP No. 27/2022</div>
        <div class="text-[11px] text-[#737373] mt-1 font-medium">Enkripsi SHA-256 Naskah</div>
      </div>

      <div class="p-4 rounded-[14px] bg-white border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] hover:border-[#d4d4d4] transition-all duration-150 ease-out">
        <div class="flex items-center justify-between mb-2">
          <div class="w-8 h-8 rounded-full bg-[#ededed] border border-[#ededed] flex items-center justify-center text-[#262626]">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-[#ededed] text-[10px] text-[#262626] font-bold border border-[#ededed]">Fast</span>
        </div>
        <div class="text-[11px] font-bold text-[#515151] uppercase tracking-wider">Target Latensi</div>
        <div class="mt-0.5 text-sm font-extrabold text-[#262626] tabular-nums">&lt; 1.500 ms</div>
        <div class="text-[11px] text-[#737373] mt-1 font-medium">Inferensi &amp; Query DB</div>
      </div>
    </div>
  </section>
</template>
