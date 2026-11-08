<script setup lang="ts">
// Ajakan bertindak penutup beranda.
</script>

<template>
  <section class="select-none px-3 pb-16 font-sans sm:px-5 sm:pb-24" aria-label="Ajakan bertindak">
    <div class="vt-stage mx-auto max-w-[1320px] rounded-[40px] px-6 py-20 text-center sm:py-28">
      <h2 class="mx-auto max-w-3xl text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#0B0F19] sm:text-[56px]">
        Pastikan tulisanmu
        <span class="vt-accent block">benar-benar asli.</span>
      </h2>
      <p class="mx-auto mt-6 max-w-xl text-[16px] leading-[1.65] text-[#4A5266] sm:text-[18px]">
        Periksa naskah dengan tiga lapis pemeriksaan dan terima laporan yang bisa dipertanggungjawabkan.
      </p>
      <div class="mt-9">
        <router-link
          to="/dashboard"
          class="inline-flex h-[54px] cursor-pointer items-center justify-center rounded-full bg-[#0B0F19] px-9 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.98]"
        >
          Mulai periksa gratis
        </router-link>
      </div>
      <p class="mt-4 text-[13px] text-[#6B7385]">5 token gratis saat daftar. Tanpa kartu kredit.</p>
    </div>
  </section>
</template>
