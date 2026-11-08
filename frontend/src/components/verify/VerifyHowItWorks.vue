<script setup lang="ts">
const steps = [
  {
    step: "01",
    title: "Pindai Kode QR",
    desc: "Arahkan kamera ponsel pada kode QR di lembar sertifikat PDF resmi.",
  },
  {
    step: "02",
    title: "Buka Tautan Otomatis",
    desc: "Peramban akan langsung mengarahkan Anda ke portal validasi ini.",
  },
  {
    step: "03",
    title: "Pencocokan UUID Resmi",
    desc: "Sistem mencocokkan UUID dokumen dengan catatan audit resmi.",
  },
];

const cards = [
  {
    badge: "KODE UUID AUDIT",
    title: "Pencocokan UUID Sertifikat",
    desc: "Sistem mencocokkan kode UUID 36-karakter dari dokumen PDF dengan basis data audit resmi VeriText AI.",
  },
  {
    badge: "INTEGRITAS NASKAH",
    title: "Ringkasan Hash SHA-256",
    desc: "Setiap naskah dicatat dengan sidik jari digital hash SHA-256 untuk memverifikasi konsistensi dokumen pengujian.",
  },
  {
    badge: "PRIVASI NASKAH",
    title: "Privasi Naskah Terjaga",
    desc: "Naskah pengguna tidak pernah disimpan ke korpus publik dan seluruh riwayat sertifikat dapat dihapus permanen.",
  },
];
</script>

<template>
  <div class="space-y-6 font-sans">
    <!-- Cara Kerja 3 Langkah -->
    <div class="bg-white rounded-2xl sm:rounded-3xl p-6 sm:p-7 border border-[#E4E8F0] shadow-[0_4px_20px_rgba(138,152,184,0.06)] space-y-5">
      <div>
        <span class="text-[11px] font-bold text-[#1560BD] uppercase tracking-wider">Panduan Pemeriksaan</span>
        <h3 class="text-base sm:text-lg font-bold text-[#0B0F19] mt-1">Cara Kerja Verifikasi Sertifikat</h3>
        <p class="text-xs sm:text-sm text-[#5B6475] mt-0.5">Validasi keaslian laporan audit naskah dapat dilakukan dalam 3 langkah mudah:</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
        <div
          v-for="item in steps"
          :key="item.step"
          class="border border-[#E4E8F0] rounded-xl sm:rounded-2xl p-4 sm:p-5 bg-slate-50/50 flex flex-col justify-between space-y-3"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-[#1560BD] tabular-nums bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
              Langkah {{ item.step }}
            </span>
          </div>
          <div>
            <h4 class="text-sm font-bold text-[#0B0F19]">{{ item.title }}</h4>
            <p class="text-xs text-[#5B6475] mt-1.5 leading-relaxed">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 3 Kartu Klaim Integritas Sesuai Backend -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
      <div
        v-for="card in cards"
        :key="card.title"
        class="bg-white rounded-2xl sm:rounded-3xl p-5 sm:p-6 border border-[#E4E8F0] shadow-[0_4px_20px_rgba(138,152,184,0.06)] flex flex-col justify-between space-y-3"
      >
        <span class="text-[10px] font-bold text-[#1560BD] uppercase tracking-wider">{{ card.badge }}</span>
        <div>
          <h4 class="text-sm font-bold text-[#0B0F19]">{{ card.title }}</h4>
          <p class="text-xs text-[#5B6475] mt-1.5 leading-relaxed">{{ card.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
