<script setup lang="ts">
// Footer.vue - Sesuai spesifikasi build_landing.py:seg_footer() dan landing--default-idle.svg
</script>

<template>
  <footer
    class="w-full border-t border-[#E4E8F0] mt-16 sm:mt-24 select-none font-sans"
    aria-label="Footer Resmi VeriText AI"
  >
    <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 pt-14 sm:pt-16 pb-12">
      <!-- Grid 2 Kolom: Brand & Deskripsi (Kiri) vs Tautan Singkat (Kanan) -->
      <div class="flex flex-col md:flex-row md:items-start justify-between gap-10 lg:gap-16">
        
        <!-- Kolom Kiri: Brand dan Deskripsi Sistem (Sesuai SVG x=75.2) -->
        <div class="max-w-2xl space-y-4">
          <!-- Wordmark merek -->
          <router-link
            to="/"
            class="inline-block text-[22px] font-bold text-[#0B0F19] tracking-tight font-sans focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1A73D9] rounded"
          >
            VeriText AI
          </router-link>

          <!-- Deskripsi Platform 3 Baris Sesuai Desain Resmi -->
          <p class="text-[14.5px] text-[#5B6475] leading-relaxed font-normal font-sans">
            Platform audit orisinalitas naskah dengan pemeriksaan kata, makna, dan gaya tulisan.
          </p>
        </div>

        <!-- Kolom Kanan: Tautan Singkat (Sesuai SVG x=1075.6) -->
        <div class="md:min-w-[200px] lg:min-w-[240px] space-y-3.5">
          <h5 class="text-[14px] font-semibold uppercase tracking-[0.8px] text-[#0B0F19] font-sans">
            TAUTAN SINGKAT
          </h5>
          <ul class="text-[15px] space-y-2.5 text-[#5B6475] font-sans">
            <li>
              <router-link
                to="/dashboard"
                class="hover:text-[#1A73D9] transition-colors inline-block focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1A73D9] rounded"
              >
                Dashboard Pengujian
              </router-link>
            </li>
            <li>
              <router-link
                to="/billing"
                class="hover:text-[#1A73D9] transition-colors inline-block focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1A73D9] rounded"
              >
                Paket Kuota Token
              </router-link>
            </li>
            <li>
              <router-link
                to="/verify"
                class="hover:text-[#1A73D9] transition-colors inline-block focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1A73D9] rounded"
              >
                Verifikasi Sertifikat
              </router-link>
            </li>
          </ul>
        </div>

      </div>

      <!-- Hairline Separator Bawah (Sesuai SVG y=4872.9) -->
      <div class="border-t border-[#E4E8F0] mt-12 pt-6">
        <p class="text-[13px] text-[#5B6475] font-normal font-sans">
          &copy; 2026 Tim Pengembang VeriText AI. Seluruh hak dilindungi.
        </p>
      </div>
    </div>
  </footer>
</template>
