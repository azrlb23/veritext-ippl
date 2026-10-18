<script setup lang="ts">
interface Props {
  isValid: boolean;
  uuid: string;
}

defineProps<Props>();
</script>

<template>
  <div
    class="text-center p-8 rounded-[14px] bg-white border border-[#ededed] shadow-audyr-subtle space-y-3 transition-all"
  >
    <div
      class="inline-flex items-center justify-center w-12 h-12 rounded-full text-xl font-bold mb-2 border"
      :class="isValid ? 'bg-audyr-mint-whisper text-[#065f46] border-[#a7f3d0]' : 'bg-red-50 text-red-700 border-red-200'"
    >
      {{ isValid ? "✓" : "✗" }}
    </div>

    <h1
      class="text-xl sm:text-2xl font-bold tracking-tight text-audyr-ink"
      :class="{ '!text-red-700': !isValid }"
    >
      {{ isValid ? "SERTIFIKAT TERVERIFIKASI ASLI" : "SERTIFIKAT TIDAK VALID" }}
    </h1>

    <p class="text-xs sm:text-sm text-audyr-ash max-w-lg mx-auto leading-relaxed">
      {{
        isValid
          ? "Hasil audit ini telah divalidasi secara kriptografis oleh sistem VeriText AI dan tercatat resmi dalam ledger sistem."
          : "Sertifikat tidak ditemukan atau naskah telah dihapus permanen oleh pemilik sesuai UU Perlindungan Data Pribadi."
      }}
    </p>

    <div class="text-[11px] font-mono text-audyr-ash pt-1">
      Kode Verifikasi: <span class="font-bold text-audyr-ink">{{ uuid }}</span>
    </div>
  </div>
</template>
