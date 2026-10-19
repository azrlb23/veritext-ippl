<script setup lang="ts">
interface Props {
  isValid: boolean;
  uuid: string;
}

defineProps<Props>();
</script>

<template>
  <div
    class="text-center p-8 sm:p-10 rounded-[24px] bg-white border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.06)] space-y-3.5 transition-all"
  >
    <div
      class="inline-flex items-center justify-center w-12 h-12 rounded-full mb-1 border"
      :class="isValid ? 'bg-[#ecfdf5] text-[#065f46] border-[#a7f3d0]' : 'bg-red-50 text-red-700 border-red-200'"
    >
      <svg v-if="isValid" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
      </svg>
      <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </div>

    <h1
      class="font-serif text-2xl sm:text-3xl font-normal tracking-tight text-[#17191c]"
      :class="{ '!text-red-700': !isValid }"
    >
      {{ isValid ? "Sertifikat Terverifikasi Asli" : "Sertifikat Tidak Valid" }}
    </h1>

    <p class="text-xs sm:text-sm text-[#777b86] max-w-lg mx-auto leading-relaxed font-normal">
      {{
        isValid
          ? "Hasil audit ini telah divalidasi secara kriptografis oleh sistem VeriText AI dan tercatat resmi dalam ledger sistem."
          : "Sertifikat tidak ditemukan atau naskah telah dihapus permanen oleh pemilik sesuai UU Perlindungan Data Pribadi."
      }}
    </p>

    <div class="text-[11px] text-[#777b86] pt-1">
      Kode Verifikasi: <span class="font-medium text-[#17191c] tabular-nums">{{ uuid }}</span>
    </div>
  </div>
</template>
