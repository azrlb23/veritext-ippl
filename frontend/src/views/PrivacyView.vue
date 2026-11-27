<script setup lang="ts">
const sections = [
  {
    title: "1. Kepatuhan UU PDP No. 27/2022",
    body: "VeriText AI memproses data pribadi dan naskah pengguna berdasarkan prinsip keterbukaan, tujuan yang sah, serta perlindungan hak subjek data sesuai Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi.",
  },
  {
    title: "2. Zero Auto-Ingestion (Naskah Tidak Masuk Korpus)",
    body: "Setiap naskah yang Anda unggah untuk diaudit bersifat rahasia dan tidak pernah dimasukkan secara otomatis ke dalam bank korpus pembanding (corpus_documents). Naskah Anda tidak akan dijadikan rujukan untuk pemeriksaan pengguna lain.",
  },
  {
    title: "3. Hard-Delete Cascade Secara Permanen",
    body: "Saat Anda menghapus dokumen dari halaman Riwayat atau menghapus akun, sistem mengeksekusi penghapusan permanen (hard-delete cascade) terhadap berkas fisik di server beserta seluruh entri pada tabel documents, audit_tasks, audit_sentences, audit_reports, chat_sessions, dan chat_messages.",
  },
  {
    title: "4. Enkripsi & Pembatasan Akses",
    body: "Kredensial akun diamankan menggunakan hashing kriptografis, komunikasi dilindungi oleh enkripsi transport, dan peran ADMIN dibatasi secara ketat pada pemantauan sistem bersifat baca-saja (read-only) tanpa akses untuk mengubah data pengguna atau mengunduh naskah pribadi Anda.",
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
          Kebijakan Privasi VeriText AI
        </h1>
        <p class="mt-3 text-[15px] leading-[1.6] text-[#4B4757]">
          Komitmen kami menjaga kerahasiaan naskah akademik, identitas pengguna, dan kepastian penghapusan data Anda.
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
