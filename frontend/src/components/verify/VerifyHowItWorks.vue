<script setup lang="ts">
import VerifyFlow from "./VerifyFlow.vue";

const steps = [
  { n: "01", title: "Pindai kode QR", desc: "Arahkan kamera ponsel ke kode QR di lembar sertifikat PDF." },
  { n: "02", title: "Halaman terbuka sendiri", desc: "Peramban membawa Anda ke sini dengan kode yang sudah terisi." },
  { n: "03", title: "Cocokkan dengan catatan", desc: "Kode dicocokkan dengan catatan audit resmi, lalu hasilnya tampil." },
];

const notes = [
  { title: "Kode UUID", text: "Kode 36 karakter di sertifikat dicocokkan dengan catatan audit VeriText AI." },
  { title: "Ringkasan hash", text: "Setiap naskah dicatat dengan ringkasan hash SHA-256 agar konsistensinya bisa diperiksa." },
  { title: "Privasi naskah", text: "Naskah tidak masuk korpus publik dan riwayat sertifikat dapat dihapus permanen." },
];
</script>

<template>
  <div class="space-y-16 font-sans sm:space-y-24">
    <VerifyFlow />

    <div class="grid gap-9 md:grid-cols-3 md:gap-8">
      <div v-for="s in steps" :key="s.n" class="flex items-start gap-5 md:block">
        <span class="vt-accent shrink-0 text-[44px] leading-none tracking-[-0.04em]">{{ s.n }}</span>
        <div class="md:mt-4">
          <h3 class="text-[19px] font-semibold tracking-[-0.02em] text-[#14111C]">{{ s.title }}</h3>
          <p class="mt-1.5 max-w-[320px] text-[15px] leading-[1.65] text-[#4B4757]">{{ s.desc }}</p>
        </div>
      </div>
    </div>

    <div class="grid gap-8 md:grid-cols-3">
      <div v-for="n in notes" :key="n.title">
        <h4 class="text-[15px] font-semibold text-[#14111C]">{{ n.title }}</h4>
        <p class="mt-2 max-w-[300px] text-[14px] leading-[1.65] text-[#4B4757]">{{ n.text }}</p>
      </div>
    </div>
  </div>
</template>
