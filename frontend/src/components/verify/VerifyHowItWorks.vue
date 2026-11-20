<script setup lang="ts">
import VerifyFlow from "./VerifyFlow.vue";

const steps = [
  { n: "01", title: "Pindai kode QR", desc: "Arahkan kamera ponsel ke kode QR di lembar sertifikat PDF." },
  { n: "02", title: "Halaman terbuka sendiri", desc: "Peramban membawa Anda ke sini dengan kode yang sudah terisi." },
  { n: "03", title: "Cocokkan dengan catatan", desc: "Kode dicocokkan dengan catatan audit resmi, lalu hasilnya tampil." },
];
</script>

<template>
  <div class="space-y-12 font-sans sm:space-y-16">
    <VerifyFlow />

    <div class="grid gap-8 border-t border-[#E6ECEB] pt-10 md:grid-cols-3 md:gap-10">
      <div v-for="s in steps" :key="s.n" class="flex items-start gap-4 md:block">
        <span class="shrink-0 text-[32px] font-light leading-none tracking-[-0.04em] text-[#0F766E]">{{ s.n }}</span>
        <div class="md:mt-3">
          <h3 class="text-[17px] font-semibold tracking-[-0.02em] text-[#14111C]">{{ s.title }}</h3>
          <p class="mt-1.5 text-[14.5px] leading-[1.6] text-[#4B4757]">{{ s.desc }}</p>
        </div>
      </div>
    </div>

    <p class="text-[13.5px] leading-[1.6] text-[#5E5A6B]">
      Setiap sertifikat dicocokkan menggunakan kode UUID 36 karakter dan ringkasan hash SHA-256 secara privat tanpa memasukkan naskah ke korpus publik.
    </p>
  </div>
</template>
