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
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-[14px] border border-[#ededed] shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-xs font-medium text-[#737373] mr-1">Kategori:</span>
      <button
        v-for="cat in categories"
        :key="cat"
        type="button"
        @click="emit('update:selectedCategory', cat)"
        class="px-3 py-1.5 rounded-[4px] text-xs font-medium tracking-tight transition-all"
        :class="
          selectedCategory === cat
            ? 'bg-[#262626] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.16),0_1px_2px_rgba(0,0,0,0.24)]'
            : 'bg-[#fafafa] hover:bg-[#ededed] text-[#515151] border border-[#ededed]'
        "
      >
        {{ cat }}
      </button>
    </div>

    <div class="flex items-center space-x-3">
      <div class="relative flex-grow sm:w-64">
        <input
          :value="searchQuery"
          @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text"
          placeholder="Cari judul koleksi korpus..."
          class="w-full px-3.5 py-1.5 pl-8 rounded-[4px] border border-[#ededed] text-xs text-[#262626] bg-white placeholder-[#929292] focus:outline-none focus:ring-1 focus:ring-[#262626] focus:border-[#262626]"
        />
        <span class="absolute left-2.5 top-2 text-[#929292] text-xs">🔍</span>
      </div>

      <Button
        variant="primary"
        size="sm"
        @click="emit('openUploadModal')"
      >
        <template #prefix>
          <span>+</span>
        </template>
        Unggah ZIP
      </Button>
    </div>
  </div>
</template>
