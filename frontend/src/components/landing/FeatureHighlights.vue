<template>
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8" aria-label="Spesifikasi Arsitektur dan Kepatuhan">
    <div class="bg-white rounded-[18px] border border-[#ededed] p-6 sm:p-8 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-6">
      <div class="max-w-3xl space-y-3">
        <!-- Mint Whisper Compliance Badge -->
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium uppercase tracking-wider bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]">
          <span>Standar Kepatuhan &amp; Arsitektur</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-semibold text-[#262626] tracking-[-0.025em]">
          Kepatuhan Privasi Dokumen &amp; Standar Akademik Nasional
        </h2>
        <p class="text-sm text-[#686868] leading-relaxed">
          VeriText AI mengimplementasikan Clean Architecture dengan pemisahan domain logic yang ketat, kepatuhan penuh terhadap Undang-Undang Perlindungan Data Pribadi (UU PDP No. 27/2022), enkripsi SHA-256 untuk sidik jari naskah, dan sertifikat QR kriptografis yang dapat diverifikasi publik tanpa kebocoran data sensitif.
        </p>
      </div>

      <!-- Core Performance & Compliance Metrics (Audyr 14px Card Style) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <div class="border border-[#ededed] hover:border-[#d4d4d4] p-5 rounded-[14px] bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] transition-all duration-150 ease-out space-y-1.5">
          <div class="text-2xl font-semibold font-mono text-[#262626] tabular-nums">&lt; 1.500 ms</div>
          <div class="text-xs font-semibold text-[#262626]">Latensi Query pgvector</div>
          <p class="text-xs text-[#686868] leading-relaxed">Pencarian kemiripan vektor HNSW berkecepatan tinggi dengan metrik jarak kosinus.</p>
        </div>
        <div class="border border-[#ededed] hover:border-[#d4d4d4] p-5 rounded-[14px] bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] transition-all duration-150 ease-out space-y-1.5">
          <div class="text-2xl font-semibold font-mono text-[#059669] tabular-nums">100%</div>
          <div class="text-xs font-semibold text-[#262626]">Kepatuhan UU PDP No. 27/2022</div>
          <p class="text-xs text-[#686868] leading-relaxed">Jaminan hak penghapusan permanen dokumen naskah (Right to Erasure) dari korpus.</p>
        </div>
        <div class="border border-[#ededed] hover:border-[#d4d4d4] p-5 rounded-[14px] bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-[0_1px_2px_rgba(0,0,0,0.06)] transition-all duration-150 ease-out space-y-1.5">
          <div class="text-2xl font-semibold font-mono text-[#262626] tabular-nums">UUID v4</div>
          <div class="text-xs font-semibold text-[#262626]">Sertifikat Kriptografis</div>
          <p class="text-xs text-[#686868] leading-relaxed">Verifikasi publik instan via scan QR code tanpa mewajibkan autentikasi akun.</p>
        </div>
      </div>

      <!-- High-Density Architecture Specification Grid (Audyr 8px Sub-Cards) -->
      <div class="pt-5 border-t border-[#ededed] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        <div class="p-3.5 rounded-[8px] border border-[#ededed] bg-[#fafafa] space-y-1 transition-colors duration-150 ease-out">
          <div class="font-mono font-semibold text-[#262626] text-[11px] uppercase tracking-wider">Clean Architecture</div>
          <p class="text-[#686868] text-[11px] leading-normal">Pemisahan lapis Domain, Application, dan Infrastructure yang modular &amp; testable.</p>
        </div>
        <div class="p-3.5 rounded-[8px] border border-[#ededed] bg-[#fafafa] space-y-1 transition-colors duration-150 ease-out">
          <div class="font-mono font-semibold text-[#262626] text-[11px] uppercase tracking-wider">Enkripsi SHA-256</div>
          <p class="text-[#686868] text-[11px] leading-normal">Sidik jari dokumen dianonimisasi dengan hash satu arah tanpa kompromi integritas data.</p>
        </div>
        <div class="p-3.5 rounded-[8px] border border-[#ededed] bg-[#fafafa] space-y-1 transition-colors duration-150 ease-out">
          <div class="font-mono font-semibold text-[#262626] text-[11px] uppercase tracking-wider">Async Workers</div>
          <p class="text-[#686868] text-[11px] leading-normal">Celery queue didukung Redis broker untuk pemrosesan naskah paralel non-blocking.</p>
        </div>
        <div class="p-3.5 rounded-[8px] border border-[#ededed] bg-[#fafafa] space-y-1 transition-colors duration-150 ease-out">
          <div class="font-mono font-semibold text-[#262626] text-[11px] uppercase tracking-wider">Standar Dikti</div>
          <p class="text-[#686868] text-[11px] leading-normal">Selaras dengan pedoman integritas akademik dan etika publikasi ilmiah nasional.</p>
        </div>
      </div>
    </div>
  </section>
</template>
