<script setup lang="ts">
import { ref, computed } from "vue";
import {
  CorpusStatsGrid,
  CorpusFilterBar,
  CorpusTable,
  CorpusUploadModal,
  type CorpusItemData,
} from "../components/corpus";
import { useModal, useNotification } from "../composables";

const { showNotification } = useNotification();
const { isOpen: isUploadModalOpen, open: openUploadModal, close: closeUploadModal } = useModal();

const selectedCategory = ref("SEMUA");
const searchQuery = ref("");
const isIngesting = ref(false);

const corpusList = ref<CorpusItemData[]>([
  {
    id: "corp-1",
    title: "Kumpulan Jurnal Rekayasa Perangkat Lunak 2024",
    category: "Informatika",
    academic_year: "2024/2025",
    total_chunks: 1420,
    status: "INDEXED",
    created_at: "2026-09-15",
  },
  {
    id: "corp-2",
    title: "Prosiding Seminar Nasional Sistem Informasi & Kecerdasan Buatan",
    category: "Sistem Informasi",
    academic_year: "2025/2026",
    total_chunks: 3890,
    status: "INDEXED",
    created_at: "2026-10-01",
  },
  {
    id: "corp-3",
    title: "Skripsi & Tesis Departemen Ilmu Komputer Periode Genap",
    category: "Ilmu Komputer",
    academic_year: "2025/2026",
    total_chunks: 520,
    status: "INDEXING",
    created_at: "2026-10-10",
  },
]);

const filteredCorpusList = computed(() => {
  return corpusList.value.filter((item) => {
    const matchesCategory =
      selectedCategory.value === "SEMUA" || item.category === selectedCategory.value;
    const matchesSearch =
      !searchQuery.value.trim() ||
      item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (item.category && item.category.toLowerCase().includes(searchQuery.value.toLowerCase()));
    return matchesCategory && matchesSearch;
  });
});

const totalChunksCount = computed(() =>
  corpusList.value.reduce((acc, curr) => acc + (curr.total_chunks || 0), 0)
);

function handleBulkIngest(payload: { title: string; category: string; academicYear: string }) {
  isIngesting.value = true;
  setTimeout(() => {
    corpusList.value.unshift({
      id: `corp-${Date.now()}`,
      title: payload.title.replace(".zip", ""),
      category: payload.category,
      academic_year: payload.academicYear,
      total_chunks: 0,
      status: "PENDING_INDEX",
      created_at: "Baru saja",
    });
    isIngesting.value = false;
    closeUploadModal();

    showNotification(
      `Arsip "${payload.title}" berhasil diantrekan ke Celery worker untuk ekstraksi embedding HNSW pgvector.`,
      "success",
      "Ingest Berhasil"
    );
  }, 600);
}

function handleDeleteItem(id: string) {
  const idx = corpusList.value.findIndex((c) => c.id === id);
  if (idx !== -1) {
    const title = corpusList.value[idx].title;
    corpusList.value.splice(idx, 1);
    showNotification(`Koleksi korpus "${title}" telah dihapus.`, "info");
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-2xl sm:text-3xl font-extrabold text-audyr-ink tracking-tight">
        Bank Dokumen Korpus Pembanding
      </h1>
      <p class="text-xs sm:text-sm text-audyr-ash mt-1">
        Koleksi repositori naskah akademik terindeks <span class="italic font-bold text-audyr-ink">pgvector HNSW (384D)</span> &amp; <span class="italic font-bold text-audyr-ink">Rabin-Karp Winnowing</span> untuk pembandingan leksikal &amp; semantik.
      </p>
    </div>

    <!-- Stats Grid -->
    <CorpusStatsGrid
      :totalDocs="corpusList.length"
      :totalChunks="totalChunksCount"
      indexStatus="Aktif & Sinkron"
    />

    <!-- Filters Bar -->
    <CorpusFilterBar
      v-model:selectedCategory="selectedCategory"
      v-model:searchQuery="searchQuery"
      @openUploadModal="openUploadModal"
    />

    <!-- Corpus Repositories Table -->
    <CorpusTable
      :items="filteredCorpusList"
      @deleteItem="handleDeleteItem"
    />

    <!-- Upload ZIP Modal -->
    <CorpusUploadModal
      :isOpen="isUploadModalOpen"
      :loading="isIngesting"
      @close="closeUploadModal"
      @submit="handleBulkIngest"
    />
  </div>
</template>
