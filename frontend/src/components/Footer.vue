<template>
  <footer class="bg-white border-t border-[#ededed] mt-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div class="md:col-span-2 space-y-3">
          <div class="flex items-center space-x-2.5">
            <span class="w-6 h-6 rounded-[4px] bg-[#262626] text-white font-extrabold flex items-center justify-center text-xs">V</span>
            <span class="font-extrabold text-[#262626] tracking-tight text-base">VeriText <span class="italic font-bold text-audyr-slate">AI</span></span>
          </div>
          <p class="text-xs text-[#686868] max-w-sm leading-relaxed">
            Sistem Deteksi Plagiarisme Cerdas Berbasis Arsitektur <span class="italic font-bold text-[#262626]">Hybrid Lexical &amp; Semantic AI Engine</span> dengan Pipa Pemrosesan 4-Tier untuk Mata Kuliah Implementasi Perangkat Lunak (IPPL).
          </p>
          <div class="text-xs text-[#737373]">
            Kepatuhan Privasi Dokumen: <span class="italic font-bold text-[#262626]">UU Perlindungan Data Pribadi (UU PDP) No. 27/2022</span>
          </div>
        </div>

        <div>
          <h5 class="text-xs font-extrabold uppercase tracking-wider text-[#262626] mb-3">Arsitektur &amp; Teknologi</h5>
          <ul class="text-xs space-y-2 text-[#686868]">
            <li>FastAPI + Clean Architecture</li>
            <li>PostgreSQL 16 + pgvector HNSW</li>
            <li>Winnowing Lexical Fingerprinting</li>
            <li>MiniLM-L12-v2 Transformers</li>
            <li>Celery Worker + Redis</li>
          </ul>
        </div>

        <div>
          <h5 class="text-xs font-extrabold uppercase tracking-wider text-[#262626] mb-3">Tautan Singkat</h5>
          <ul class="text-xs space-y-2 text-[#686868]">
            <li><router-link to="/dashboard" class="hover:text-[#262626] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] rounded-[4px] px-1 -mx-1">Dashboard Pengujian</router-link></li>
            <li><router-link to="/corpus" class="hover:text-[#262626] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] rounded-[4px] px-1 -mx-1">Repositori Korpus</router-link></li>
            <li><router-link to="/billing" class="hover:text-[#262626] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] rounded-[4px] px-1 -mx-1">Paket Kuota Token</router-link></li>
            <li><router-link to="/verify/sample" class="hover:text-[#262626] transition-colors duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[#262626] rounded-[4px] px-1 -mx-1">Verifikasi Sertifikat</router-link></li>
          </ul>
        </div>
      </div>

      <div class="border-t border-[#ededed] mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-[#737373]">
        <div>&copy; 2026 Tim Pengembang VeriText AI. Hak Cipta Dilindungi Undang-Undang.</div>
        <div class="mt-2 sm:mt-0 tabular-nums text-[11px] text-[#737373]">Versi <span class="font-extrabold text-[#262626]">v1.0.0-rc1</span> | Mode <span class="italic font-bold text-[#262626]">Sandbox IPPL</span></div>
      </div>
    </div>
  </footer>
</template>
