<script setup lang="ts">
const sections = [
  {
    title: "1. Model 3-Role SaaS (FREE, PREMIUM, ADMIN)",
    body: "Akun FREE memperoleh 5 Token gratis dan 3x kuota trial Asisten AI dengan batas unggah hingga 2.500 kata per dokumen serta laporan view-only di peramban. Akun PREMIUM aktif otomatis setelah transaksi berhasil, mendukung naskah hingga 15 MB, unduhan sertifikat PDF ber-QR Code, dan Asisten AI penuh. Peran ADMIN murni bertugas memantau operasional secara read-only.",
  },
  {
    title: "2. Skema Token & Token Cap",
    body: "Biaya audit naskah dihitung dengan rumus min(5, ceil(Jumlah Kata / 2.500)) Token, sehingga naskah panjang seperti skripsi atau tesis dikenai batas maksimal 5 Token per audit. Setelah kuota trial habis, 1 Token bernilai 10x interaksi chat atau parafrase kalimat/paragraf, serta 1 Token per 2 halaman untuk parafrase batch halaman penuh.",
  },
  {
    title: "3. Transaksi Pembayaran Midtrans Snap",
    body: "Pembelian token tersedia secara satuan (Rp 2.000/token, minimal 5 Token) maupun paket bundling (Starter 15 Token, Skripsi Pro 50 Token, Riset Intensif 150 Token) melalui Midtrans Snap. Penambahan saldo token dan aktivasi status PREMIUM diproses otomatis dan atomik setelah notifikasi webhook berstatus settlement atau capture terverifikasi.",
  },
  {
    title: "4. Sifat Probabilistik Deteksi AI",
    body: "Analisis kesamaan dan deteksi pola penulisan AI (termasuk sinyal struktural WP:AISIGNS dan penyaringan Two-Stage Funnel) bersifat probabilistik sebagai alat bantu evaluasi akademik. Hasil skor komposit dan penanda kalimat bukan merupakan vonis hukum mutlak dan wajib ditinjau ulang oleh penulis atau penilai.",
  },
];
</script>

<template>
  <div class="mx-auto max-w-[920px] px-4 pb-20 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-6">
      <router-link
        to="/"
        class="vt-btn-light inline-flex min-h-[44px] items-center gap-2 rounded-full px-5 text-[14px] font-semibold text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6" /></svg>
        Kembali ke Beranda
      </router-link>
    </div>

    <article class="rounded-[32px] border border-[#E8ECEB] bg-white p-6 shadow-float sm:p-10">
      <header class="border-b border-[#E8ECEB] pb-6">
        <h1 class="text-[28px] font-semibold leading-[1.15] tracking-[-0.035em] text-[#14111C] sm:text-[34px]">
          Ketentuan Layanan VeriText AI
        </h1>
        <p class="mt-3 text-[15px] leading-[1.6] text-[#4B4757]">
          Aturan penggunaan layanan audit orisinalitas, perhitungan token, pembayaran, dan interpretasi skor deteksi.
        </p>
        <p class="mt-2 text-[13px] font-medium text-[#5E5A6B]">Pembaruan terakhir: November 2026</p>
      </header>

      <div class="mt-6 space-y-6">
        <section v-for="sec in sections" :key="sec.title" class="border-t border-[#E8ECEB] pt-5 first:border-t-0 first:pt-0">
          <h2 class="text-[17px] font-semibold tracking-[-0.02em] text-[#14111C]">{{ sec.title }}</h2>
          <p class="mt-2 text-[14.5px] leading-[1.7] text-[#4B4757]">{{ sec.body }}</p>
        </section>
      </div>
    </article>
  </div>
</template>
