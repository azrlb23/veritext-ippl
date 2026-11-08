<script setup lang="ts">
const links = [
  { name: "Dashboard Pengujian", to: "/dashboard" },
  { name: "Paket Kuota Token", to: "/billing" },
  { name: "Verifikasi Sertifikat", to: "/verify" },
];
</script>

<template>
  <footer class="relative mt-16 w-full select-none overflow-hidden font-sans sm:mt-24" aria-label="Footer VeriText AI">
    <div class="relative mx-auto max-w-[1240px] px-6 pt-8 sm:px-8">
      <div class="flex flex-col gap-12 md:flex-row md:items-start md:justify-between">
        <div class="max-w-md">
          <router-link
            to="/"
            class="inline-block rounded text-[24px] font-semibold tracking-[-0.04em] text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          >
            VeriText <span class="text-[#8A3FE0]">AI</span>
          </router-link>
          <p class="mt-4 text-[15px] leading-[1.65] text-[#4B4757]">
            Platform audit orisinalitas naskah dengan pemeriksaan kata, makna, dan gaya tulisan.
          </p>
          <router-link
            to="/dashboard"
            class="mt-6 inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-6 text-[13.5px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5"
          >
            Mulai periksa gratis
          </router-link>
        </div>

        <nav class="md:min-w-[220px]" aria-label="Tautan singkat">
          <h5 class="text-[13px] font-medium text-[#5E5A6B]">Tautan singkat</h5>
          <ul class="mt-4 space-y-3 text-[15px] text-[#14111C]">
            <li v-for="l in links" :key="l.to">
              <router-link
                :to="l.to"
                class="inline-block rounded transition-colors duration-200 hover:text-[#6D28D9] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
              >
                {{ l.name }}
              </router-link>
            </li>
          </ul>
        </nav>
      </div>

      <p class="mt-14 text-[13px] text-[#5E5A6B]">&copy; 2026 Tim Pengembang VeriText AI. Seluruh hak dilindungi.</p>
    </div>

    <div class="pointer-events-none relative mt-6 h-[clamp(70px,13vw,190px)] overflow-hidden text-center" aria-hidden="true">
      <span
        class="block bg-gradient-to-b from-[#8A3FE0]/30 to-transparent bg-clip-text text-[clamp(90px,21vw,320px)] font-semibold leading-[0.9] tracking-[-0.06em] text-transparent"
      >VeriText AI</span>
    </div>
  </footer>
</template>
