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
  <div class="flex flex-col gap-4 border-b border-[#E6ECEB] pb-0 lg:flex-row lg:items-end lg:justify-between">
    <div class="flex gap-6 overflow-x-auto" role="tablist" aria-label="Saring status">
      <button
        v-for="o in options"
        :key="o.key"
        type="button"
        role="tab"
        :aria-selected="filter === o.key"
        class="-mb-px shrink-0 cursor-pointer border-b-2 pb-3 text-[14px] font-semibold transition-colors focus:outline-none"
        :class="filter === o.key ? 'border-[#0F766E] text-[#14111C]' : 'border-transparent text-[#5E5A6B] hover:text-[#14111C]'"
        @click="$emit('update:filter', o.key)"
      >{{ o.label }}</button>
    </div>
    <label class="relative block pb-2 lg:w-72">
      <span class="sr-only">Cari judul naskah</span>
      <input
        :value="query"
        type="search"
        placeholder="Cari judul naskah..."
        autocomplete="off"
        class="block h-10 w-full border-0 bg-transparent text-[15px] text-[#14111C] placeholder:text-[#5E5A6B]/70 outline-none"
        @input="$emit('update:query', ($event.target as HTMLInputElement).value)"
      />
    </label>
  </div>
</template>
