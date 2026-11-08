<script setup lang="ts">
// Ilustrasi hasil per kalimat pada hero. Kalimat dan angka adalah contoh.
const rows = [
  { text: "Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.", mark: "bg-[#FEE2E2]", note: "Sumber web 94%" },
  { text: "Sebagian besar responden menyatakan puas dengan layanan tersebut.", mark: "bg-[#FFEDD5]", note: "Mirip makna 81%" },
  { text: "Penting untuk dicatat bahwa era digital membawa banyak perubahan.", mark: "bg-[#FEF3C7]", note: "Pola tulisan AI" },
  { text: "Data dikumpulkan melalui wawancara mendalam dengan sepuluh narasumber.", mark: "", note: "Sudah diperbaiki" },
];
</script>

<template>
  <div class="relative" aria-hidden="true">
    <div class="absolute -top-6 left-1/2 z-10 -translate-x-1/2 w-[calc(100%-1rem)] rounded-[18px] bg-white px-4 py-2.5 sm:w-auto sm:whitespace-nowrap text-[12.5px] text-[#14111C] shadow-lift flex items-center gap-2.5">
      <svg class="h-4 w-4 text-[#DC2626]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l9 16H3L12 3zM12 10v4M12 17.5v.01" />
      </svg>
      <span><strong class="font-semibold">Mirip sumber web.</strong> Kalimat 3 cocok 94% dengan artikel publik.</span>
    </div>

    <div class="rounded-[30px] bg-white px-4 pb-4 pt-9 shadow-float">
      <div class="flex items-center justify-between px-2 pb-3">
        <span class="text-[14px] font-semibold text-[#14111C]">Hasil per kalimat</span>
        <span class="text-[11.5px] text-[#5E5A6B]">12 kalimat diperiksa</span>
      </div>

      <div class="space-y-1">
        <div v-for="r in rows" :key="r.note" class="flex items-center justify-between gap-4 rounded-[18px] px-3 py-3 text-left even:bg-[#F7F4FB]">
          <p class="min-w-0 text-[13px] leading-[1.55] text-[#14111C]">
            <span class="rounded-[6px] px-1 py-0.5" :class="r.mark">{{ r.text }}</span>
          </p>
          <span class="hidden shrink-0 text-[12px] text-[#5E5A6B] sm:block">{{ r.note }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
