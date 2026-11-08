<script setup lang="ts">
export type RiwayatFilter = "ALL" | "SUCCESS" | "ACTIVE" | "FAILED";

defineProps<{ filter: RiwayatFilter; query: string }>();
defineEmits<{ (e: "update:filter", v: RiwayatFilter): void; (e: "update:query", v: string): void }>();

const options: { key: RiwayatFilter; label: string }[] = [
  { key: "ALL", label: "Semua" },
  { key: "SUCCESS", label: "Selesai" },
  { key: "ACTIVE", label: "Diproses" },
  { key: "FAILED", label: "Gagal" },
];
</script>

<template>
  <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
    <div class="grid grid-cols-4 gap-1 rounded-full bg-[#F3EEFA] p-1 sm:inline-flex" role="tablist" aria-label="Saring status">
      <button
        v-for="o in options"
        :key="o.key"
        type="button"
        role="tab"
        :aria-selected="filter === o.key"
        class="inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-2 text-[14px] sm:px-5 font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        :class="filter === o.key ? 'bg-white text-[#14111C] shadow-lift' : 'text-[#5E5A6B] hover:text-[#14111C]'"
        @click="$emit('update:filter', o.key)"
      >{{ o.label }}</button>
    </div>
    <label class="relative block lg:w-72">
      <span class="text-[13px] font-medium text-[#5E5A6B]">Cari judul naskah</span>
      <input
        :value="query"
        type="search"
        autocomplete="off"
        class="block h-11 w-full border-0 border-b-2 border-[#14111C]/10 bg-transparent text-[16px] text-[#14111C] outline-none transition-colors focus:border-[#8A3FE0]"
        @input="$emit('update:query', ($event.target as HTMLInputElement).value)"
      />
    </label>
  </div>
</template>
