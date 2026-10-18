<script setup lang="ts">
import Button from "../common/Button.vue";

interface Props {
  categories?: string[];
  selectedCategory: string;
  searchQuery: string;
}

withDefaults(defineProps<Props>(), {
  categories: () => ["SEMUA", "Informatika", "Sistem Informasi", "Ilmu Komputer", "Teknik Elektro"],
  selectedCategory: "SEMUA",
  searchQuery: "",
});

const emit = defineEmits<{
  (e: "update:selectedCategory", val: string): void;
  (e: "update:searchQuery", val: string): void;
  (e: "openUploadModal"): void;
}>();
</script>

<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 sm:p-4 rounded-[14px] border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
    <!-- Left: Category Dropdown Selector -->
    <div class="flex items-center space-x-2">
      <label for="category-select" class="text-xs font-bold text-[#686868] whitespace-nowrap">
        Kategori:
      </label>
      <div class="relative min-w-[190px]">
        <select
          id="category-select"
          :value="selectedCategory"
          @change="emit('update:selectedCategory', ($event.target as HTMLSelectElement).value)"
          class="w-full appearance-none bg-[#fafafa] hover:bg-[#f5f5f5] border border-[#ededed] focus:border-[#262626] rounded-[4px] pl-3 pr-8 py-1.5 text-xs font-bold text-[#262626] focus:outline-none focus:ring-1 focus:ring-[#262626] transition-colors cursor-pointer tracking-tight"
        >
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat === 'SEMUA' ? 'Semua Kategori Bidang' : cat }}
          </option>
        </select>
        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-[#686868]">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Right: Search Input & Upload ZIP Button -->
    <div class="flex items-center space-x-2.5 flex-grow sm:flex-grow-0 justify-end">
      <div class="relative flex-grow sm:w-72">
        <input
          :value="searchQuery"
          @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text"
          placeholder="Cari judul koleksi naskah..."
          class="w-full px-3 py-1.5 pl-8 rounded-[4px] border border-[#ededed] text-xs text-[#262626] bg-[#fafafa] focus:bg-white placeholder-[#929292] focus:outline-none focus:ring-1 focus:ring-[#262626] focus:border-[#262626] transition-colors"
        />
        <svg class="w-3.5 h-3.5 absolute left-2.5 top-2 text-[#929292]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <Button
        variant="primary"
        size="sm"
        @click="emit('openUploadModal')"
        class="whitespace-nowrap"
      >
        <template #prefix>
          <span>+</span>
        </template>
        Unggah ZIP
      </Button>
    </div>
  </div>
</template>
