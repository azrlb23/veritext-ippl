<script setup lang="ts">
import { ref } from "vue";

// Interaktif: pilihan gaya parafrase bisa diklik secara langsung.
const activeStyle = ref("Formal");
const options = [
  { style: "Formal", text: "Lonjakan harga bahan bakar mendorong inflasi naik signifikan." },
  { style: "Ringkas", text: "Harga bahan bakar naik, inflasi ikut melonjak." },
  { style: "Analitis", text: "Inflasi meningkat tajam seiring naiknya biaya energi." },
];
</script>

<template>
  <div
    class="w-[306px] rounded-[26px] bg-white p-5 shadow-float origin-left [transform:perspective(1200px)_rotateY(-24deg)_rotateZ(5deg)] transition-all duration-500 ease-out hover:[transform:perspective(1200px)_rotateY(-8deg)_rotateZ(2deg)_translateY(-8px)] hover:shadow-2xl animate-card-right cursor-default"
    aria-hidden="true"
  >
    <div class="flex items-center justify-between">
      <div class="text-[14px] font-semibold text-[#14111C]">Parafrase kalimat</div>
      <div class="text-[11px] font-medium text-[#6D28D9] bg-[#F3EEFA] px-2.5 py-0.5 rounded-full">Klik gaya</div>
    </div>

    <p class="mt-4 text-[12.5px] leading-[1.65] text-[#14111C]">
      <span class="rounded-[6px] bg-[#F1E8FC] px-1.5 py-0.5 text-[#6D28D9] font-medium transition-all duration-300">
        {{ options.find((o) => o.style === activeStyle)?.text }}
      </span>
    </p>

    <div class="mt-4 space-y-2">
      <div
        v-for="o in options"
        :key="o.style"
        class="rounded-[16px] px-3.5 py-2.5 cursor-pointer transition-all duration-200"
        :class="activeStyle === o.style ? 'bg-[#F1E8FC] shadow-sm scale-[1.02]' : 'bg-[#F5F2F9] hover:bg-[#EFEBF5]'"
        @click="activeStyle = o.style"
      >
        <div class="flex items-center justify-between">
          <span class="text-[12px] font-semibold text-[#14111C]">{{ o.style }}</span>
          <span v-if="activeStyle === o.style" class="rounded-full bg-[#14111C] px-3 py-0.5 text-[10.5px] font-semibold text-white shadow-sm transition-all">
            Aktif
          </span>
        </div>
        <p class="mt-1 text-[11.5px] leading-[1.5] text-[#4B4757]">{{ o.text }}</p>
      </div>
    </div>
  </div>
</template>
