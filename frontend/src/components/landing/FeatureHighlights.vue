<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8" aria-label="Spesifikasi Arsitektur dan Kepatuhan">
    <div class="bg-white rounded-[24px] border border-[#ededed] p-6 sm:p-10 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] space-y-8">
      <div class="max-w-3xl space-y-3">
        <!-- Mint Whisper Compliance Badge -->
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
          <span>Standar Kepatuhan &amp; Arsitektur</span>
        </div>
        <h2 class="font-serif text-2xl sm:text-3xl font-normal text-[#17191c] tracking-tight">
          Kepatuhan Privasi Dokumen &amp; <span class="italic font-normal text-[#17191c]">Standar Akademik Nasional</span>
        </h2>
        <p class="text-sm text-[#777b86] leading-relaxed font-normal">
          VeriText AI mengimplementasikan Clean Architecture dengan pemisahan domain logic yang ketat, kepatuhan penuh terhadap Undang-Undang Perlindungan Data Pribadi (<strong class="italic font-medium text-[#17191c]">UU PDP No. 27/2022</strong>), enkripsi <strong class="font-medium text-[#17191c]">SHA-256</strong> untuk sidik jari naskah, dan sertifikat QR kriptografis yang dapat diverifikasi publik tanpa kebocoran data sensitif.
        </p>
      </div>

      <!-- Core Performance & Compliance Metrics (Steep 20px Card Style) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-2">
        <div class="border border-[#ededed] hover:border-[#17191c] p-6 rounded-[20px] bg-white shadow-[0_0_0_1px_rgba(4,23,43,0.05)] transition-all duration-150 ease-out space-y-2">
          <div class="text-2xl sm:text-3xl font-normal font-serif text-[#17191c] tabular-nums">&lt; 1.500 ms</div>
          <div class="text-xs font-semibold text-[#17191c]">Latensi Query pgvector</div>
          <p class="text-xs text-[#777b86] leading-relaxed font-normal">Pencarian kemiripan vektor HNSW berkecepatan tinggi dengan metrik jarak kosinus.</p>
        </div>
        <div class="border border-[#ededed] hover:border-[#17191c] p-6 rounded-[20px] bg-white shadow-[0_0_0_1px_rgba(4,23,43,0.05)] transition-all duration-150 ease-out space-y-2">
          <div class="text-2xl sm:text-3xl font-normal font-serif text-[#059669] tabular-nums">100%</div>
          <div class="text-xs font-semibold text-[#17191c]">Kepatuhan UU PDP No. 27/2022</div>
          <p class="text-xs text-[#777b86] leading-relaxed font-normal">Jaminan hak penghapusan permanen dokumen naskah (Right to Erasure) dari korpus.</p>
        </div>
        <div class="border border-[#ededed] hover:border-[#17191c] p-6 rounded-[20px] bg-white shadow-[0_0_0_1px_rgba(4,23,43,0.05)] transition-all duration-150 ease-out space-y-2">
          <div class="text-2xl sm:text-3xl font-normal font-serif text-[#17191c] tabular-nums">UUID v4</div>
          <div class="text-xs font-semibold text-[#17191c]">Sertifikat Kriptografis</div>
          <p class="text-xs text-[#777b86] leading-relaxed font-normal">Verifikasi publik instan via scan QR code tanpa mewajibkan autentikasi akun.</p>
        </div>
      </div>

      <!-- High-Density Architecture Specification Grid (Steep 16px Sub-Cards) -->
      <div class="pt-6 border-t border-[#ededed] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 text-xs">
        <div class="p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] space-y-1.5 transition-colors duration-150 ease-out">
          <div class="font-medium text-[#17191c] text-[11px] uppercase tracking-wider">Clean Architecture</div>
          <p class="text-[#777b86] text-[11px] leading-normal font-normal">Pemisahan lapis Domain, Application, dan Infrastructure yang modular &amp; testable.</p>
        </div>
        <div class="p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] space-y-1.5 transition-colors duration-150 ease-out">
          <div class="font-medium text-[#17191c] text-[11px] uppercase tracking-wider">Enkripsi SHA-256</div>
          <p class="text-[#777b86] text-[11px] leading-normal font-normal">Sidik jari dokumen dianonimisasi dengan hash satu arah tanpa kompromi integritas data.</p>
        </div>
        <div class="p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] space-y-1.5 transition-colors duration-150 ease-out">
          <div class="font-medium text-[#17191c] text-[11px] uppercase tracking-wider">Async Workers</div>
          <p class="text-[#777b86] text-[11px] leading-normal font-normal">Celery queue didukung Redis broker untuk pemrosesan naskah paralel non-blocking.</p>
        </div>
        <div class="p-4 rounded-[16px] border border-[#ededed] bg-[#fafafb] space-y-1.5 transition-colors duration-150 ease-out">
          <div class="font-medium text-[#17191c] text-[11px] uppercase tracking-wider">Standar Dikti</div>
          <p class="text-[#777b86] text-[11px] leading-normal font-normal">Selaras dengan pedoman integritas akademik dan etika publikasi ilmiah nasional.</p>
        </div>
      </div>
    </div>
  </section>
</template>
