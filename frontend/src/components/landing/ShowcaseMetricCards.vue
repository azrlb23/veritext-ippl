<script setup lang="ts">
// Tiga kartu metrik kecil interaktif yang bisa diklik untuk memfilter naskah.
defineProps<{ activeFilter?: string; active?: boolean }>();
const emit = defineEmits<{ (e: "select", key: string): void }>();

const items = [
  {
    key: "lex",
    label: "Kecocokan kata",
    value: "10,5%",
    width: "52%",
    bar: "bg-[#EF4444]",
    track: "bg-[#D5ECE8]",
    card: "bg-[#EBF8F6] border border-[#CDEAE5] text-[#14111C]",
    sub: "text-[#4B4757]",
    tilt: "lg:-rotate-3 lg:translate-y-2",
  },
  {
    key: "sem",
    label: "Kecocokan makna",
    value: "3,8%",
    width: "19%",
    bar: "bg-[#FDBA74]",
    track: "bg-white/20",
    card: "bg-[#0F766E] text-white",
    sub: "text-white/80",
    tilt: "lg:rotate-2 lg:-translate-y-3",
  },
  {
    key: "sty",
    label: "Pola tulisan AI",
    value: "0,9%",
    width: "5%",
    bar: "bg-[#F59E0B]",
    track: "bg-[#E6F2F0]",
    card: "bg-white text-[#14111C]",
    sub: "text-[#5E5A6B]",
    tilt: "lg:-rotate-2 lg:translate-y-1",
  },
];
</script>

<template>
  <div class="flex items-end gap-3">
    <div
      v-for="m in items"
      :key="m.label"
      class="group flex-1 rounded-[22px] p-4 shadow-lift lg:w-[168px] lg:flex-none transition-all duration-300 ease-out hover:-translate-y-3 hover:rotate-0 hover:scale-105 hover:shadow-float cursor-pointer"
      :class="[m.card, m.tilt, activeFilter === m.key ? 'ring-2 ring-[#0D9488] shadow-float -translate-y-2' : '']"
      @click="emit('select', m.key)"
    >
      <div class="text-[12px] transition-colors" :class="m.sub">{{ m.label }}</div>
      <div class="mt-1 text-[26px] font-semibold tracking-[-0.03em] tabular-nums group-hover:scale-105 transition-transform origin-left">{{ m.value }}</div>
      <div class="mt-3 h-1.5 w-full rounded-full overflow-hidden" :class="m.track">
        <div class="h-1.5 rounded-full transition-all duration-700 ease-out group-hover:opacity-90" :class="m.bar" :style="{ width: active === false ? '0%' : m.width }"></div>
      </div>
    </div>
  </div>
</template>
