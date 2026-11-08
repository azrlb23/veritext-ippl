<script setup lang="ts">
// Tiga kartu metrik kecil interaktif yang bisa diklik untuk memfilter naskah.
defineProps<{ activeFilter?: string }>();
const emit = defineEmits<{ (e: "select", key: string): void }>();

const items = [
  { key: "lex", label: "Kecocokan kata", value: "10,5%", width: "52%", bar: "bg-[#EF4444]", tilt: "lg:-rotate-3 lg:translate-y-2" },
  { key: "sem", label: "Kecocokan makna", value: "3,8%", width: "19%", bar: "bg-[#F97316]", tilt: "lg:rotate-2 lg:-translate-y-3" },
  { key: "sty", label: "Pola tulisan AI", value: "0,9%", width: "5%", bar: "bg-[#EAB308]", tilt: "lg:-rotate-2 lg:translate-y-1" },
];
</script>

<template>
  <div class="flex items-end gap-3">
    <div
      v-for="m in items"
      :key="m.label"
      class="group flex-1 rounded-[22px] bg-white p-4 shadow-lift lg:w-[168px] lg:flex-none transition-all duration-300 ease-out hover:-translate-y-3 hover:rotate-0 hover:scale-105 hover:shadow-float cursor-pointer"
      :class="[m.tilt, activeFilter === m.key ? 'ring-2 ring-[#8A3FE0] shadow-float -translate-y-2' : '']"
      @click="emit('select', m.key)"
    >
      <div class="text-[12px] text-[#5E5A6B] group-hover:text-[#14111C] transition-colors">{{ m.label }}</div>
      <div class="mt-1 text-[26px] font-semibold tracking-[-0.03em] text-[#14111C] tabular-nums group-hover:scale-105 transition-transform origin-left">{{ m.value }}</div>
      <div class="mt-3 h-1.5 w-full rounded-full bg-[#EFEAF6] overflow-hidden">
        <div class="h-1.5 rounded-full transition-all duration-700 ease-out group-hover:opacity-90" :class="m.bar" :style="{ width: m.width }"></div>
      </div>
    </div>
  </div>
</template>
