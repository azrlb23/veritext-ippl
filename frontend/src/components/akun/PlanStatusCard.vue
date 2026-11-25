<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "../../stores/auth";

const authStore = useAuthStore();
const isPremium = computed(() => authStore.role === "PREMIUM");
const trialLeft = computed(() => authStore.user?.ai_trial_remaining ?? 0);
const chatLeft = computed(() => authStore.user?.ai_chat_allowance_remaining ?? 0);

const features = [
  { name: "Batas ukuran & kata naskah", free: "Maks. 2.500 kata", premium: "Hingga 15 MB (penuh)", freeOk: true },
  { name: "Deteksi 3-lapis (Leksikal, Semantik, AI)", free: "Tersedia", premium: "Tersedia", freeOk: true },
  { name: "Laporan audit interaktif di web", free: "Lihat saja (view-only)", premium: "Penuh + tulis ulang", freeOk: true },
  { name: "Unduh sertifikat PDF resmi ber-QR", free: "Tidak tersedia", premium: "Tersedia tanpa batas", freeOk: false },
  { name: "Ekspor naskah revisi (.DOCX & .PDF)", free: "Tidak tersedia", premium: "Tersedia", freeOk: false },
  { name: "Asisten AI & parafrase 3-mode", free: "Kuota trial 3 sesi", premium: "Penuh (10 pesan / token)", freeOk: true },
  { name: "Masa berlaku status & token", free: "Token tidak kedaluwarsa", premium: "Premium permanen", freeOk: true },
];
</script>

<template>
  <section class="rounded-[28px] border border-white/80 bg-white/85 p-6 shadow-[0_12px_32px_-12px_rgba(20,17,28,0.08)] backdrop-blur-sm sm:p-8" aria-labelledby="plan-judul">
    <div class="flex flex-col gap-5 border-b border-[#E6ECEB] pb-6 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="flex items-center gap-2.5">
          <h2 id="plan-judul" class="text-[20px] font-semibold tracking-[-0.025em] text-[#14111C]">Paket &amp; Hak Fitur</h2>
          <span class="text-[12.5px] font-semibold" :class="isPremium ? 'text-[#0F766E]' : 'text-[#5E5A6B]'">
            {{ isPremium ? "Premium Aktif Permanen" : "Paket Gratis" }}
          </span>
        </div>
        <p class="mt-1 text-[14px] text-[#5E5A6B]">
          {{ isPremium
            ? "Seluruh fitur naskah panjang, ekspor PDF ber-QR, dan Asisten AI telah terbuka permanen."
            : "Pembelian token pertama otomatis mengaktifkan seluruh fitur Premium tanpa biaya langganan bulanan." }}
        </p>
      </div>
      <router-link
        to="/billing"
        class="inline-flex h-11 shrink-0 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold"
        :class="isPremium ? 'vt-btn-light' : 'vt-btn-dark shadow-[0_10px_24px_-8px_rgba(17,14,24,0.38)]'"
      >{{ isPremium ? "Kelola & Isi Token" : "Upgrade ke Premium" }}</router-link>
    </div>

    <div class="grid gap-4 border-b border-[#E6ECEB] py-5 sm:grid-cols-3">
      <div>
        <p class="text-[12.5px] text-[#5E5A6B]">Saldo token aktif</p>
        <p class="mt-1 text-[22px] font-semibold tabular-nums text-[#14111C]">{{ authStore.tokenBalance }} <span class="text-[14px] font-medium text-[#0F766E]">token</span></p>
      </div>
      <div>
        <p class="text-[12.5px] text-[#5E5A6B]">Kuota trial AI</p>
        <p class="mt-1 text-[22px] font-semibold tabular-nums text-[#14111C]">{{ trialLeft }} <span class="text-[14px] font-medium text-[#5E5A6B]">/ 3 sesi</span></p>
      </div>
      <div>
        <p class="text-[12.5px] text-[#5E5A6B]">Kuota pesan Asisten AI</p>
        <p class="mt-1 text-[22px] font-semibold tabular-nums text-[#14111C]">{{ chatLeft }} <span class="text-[14px] font-medium text-[#5E5A6B]">pesan tersisa</span></p>
      </div>
    </div>

    <div class="mt-5 overflow-x-auto">
      <table class="w-full min-w-[540px] text-left text-[13.5px]">
        <thead>
          <tr class="border-b border-[#E6ECEB] text-[12.5px] font-semibold text-[#5E5A6B]">
            <th class="pb-3 pr-4">Fasilitas</th>
            <th class="pb-3 pr-4" :class="!isPremium ? 'text-[#14111C]' : ''">Gratis {{ !isPremium ? "(Aktif)" : "" }}</th>
            <th class="pb-3" :class="isPremium ? 'text-[#0F766E]' : ''">Premium {{ isPremium ? "(Aktif)" : "" }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#E6ECEB]">
          <tr v-for="f in features" :key="f.name">
            <td class="py-3 pr-4 font-medium text-[#14111C]">{{ f.name }}</td>
            <td class="py-3 pr-4" :class="f.freeOk ? 'text-[#4B4757]' : 'text-[#94A3B8]'">{{ f.free }}</td>
            <td class="py-3 font-medium" :class="isPremium ? 'text-[#0F766E]' : 'text-[#14111C]'">{{ f.premium }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
