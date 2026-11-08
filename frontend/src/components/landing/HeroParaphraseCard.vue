<script setup lang="ts">
// Ilustrasi kartu parafrase pada hero. Teks contoh.
const options = [
  { style: "Formal", text: "Lonjakan harga bahan bakar mendorong inflasi naik signifikan.", active: true },
  { style: "Ringkas", text: "Harga bahan bakar naik, inflasi ikut melonjak.", active: false },
  { style: "Analitis", text: "Inflasi meningkat tajam seiring naiknya biaya energi.", active: false },
];
</script>

<template>
  <div
    class="w-[306px] rounded-[26px] bg-white p-5 shadow-float origin-left [transform:perspective(1200px)_rotateY(-24deg)_rotateZ(5deg)]"
    aria-hidden="true"
  >
    <div class="flex items-center justify-between">
      <div class="text-[14px] font-semibold text-[#0B0F19]">Parafrase kalimat</div>
      <div class="text-[11.5px] text-[#6B7385]">3 pilihan gaya</div>
    </div>

    <p class="mt-4 text-[12.5px] leading-[1.65] text-[#0B0F19]">
      <span class="rounded-[6px] bg-[#FEE2E2] px-1 py-0.5">Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.</span>
    </p>

    <div class="mt-4 space-y-2">
      <div
        v-for="o in options"
        :key="o.style"
        class="rounded-[16px] px-3.5 py-3"
        :class="o.active ? 'bg-[#EEF3FF]' : 'bg-[#F6F7FB]'"
      >
        <div class="flex items-center justify-between">
          <span class="text-[12px] font-semibold text-[#0B0F19]">{{ o.style }}</span>
          <span v-if="o.active" class="rounded-full bg-[#0B0F19] px-3 py-1 text-[10.5px] font-semibold text-white">Terapkan</span>
        </div>
        <p class="mt-1 text-[12px] leading-[1.55] text-[#4A5266]">{{ o.text }}</p>
      </div>
    </div>
  </div>
</template>
