<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import {
  CorpusStatsGrid,
  CorpusFilterBar,
  CorpusTable,
  CorpusUploadModal,
  type CorpusItemData,
} from "../components/corpus";
import { useModal, useNotification } from "../composables";
import { useAuthStore } from "../stores/auth";
import { corpusService } from "../services/corpusService";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const { isOpen: isUploadModalOpen, open: openUploadModal, close: closeUploadModal } = useModal();

const selectedCategory = ref("SEMUA");
const searchQuery = ref("");
const isIngesting = ref(false);
const isLoading = ref(false);

const corpusList = ref<CorpusItemData[]>([]);

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

async function loadCorpus() {
  isLoading.value = true;
  try {
    const data = await corpusService.list(
      selectedCategory.value === "SEMUA" ? undefined : selectedCategory.value,
      1,
      100
    );
    if (data && Array.isArray(data.items)) {
      corpusList.value = data.items.map((item: any) => ({
        id: String(item.id),
        title: item.title || item.original_filename || "Naskah Korpus",
        category: item.category || "Umum",
        academic_year: item.academic_year || "-",
        total_chunks: item.total_chunks ?? 0,
        status: item.status || "INDEXED",
        created_at: item.created_at ? String(item.created_at).substring(0, 10) : "",
      }));
    }
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal memuat repositori korpus.",
      "error"
    );
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  if (authStore.isAuthenticated && authStore.role === "ADMIN") {
    router.replace({ path: "/admin", hash: "#corpus" });
    return;
  }
  void loadCorpus();
});

watch(selectedCategory, () => {
  void loadCorpus();
});

async function handleBulkIngest(payload: { title: string; category: string; academicYear: string; file?: File | null }) {
  if (!payload.file) {
    showNotification("Berkas arsip ZIP harus disertakan.", "warning");
    return;
  }
  isIngesting.value = true;
  try {
    await corpusService.ingest(payload.file, payload.category, payload.academicYear);
    closeUploadModal();
    showNotification(
      `Arsip "${payload.title}" berhasil diunggah dan diantrekan ke Celery worker untuk ekstraksi embedding HNSW pgvector.`,
      "success",
      "Ingest Berhasil"
    );
    await loadCorpus();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal mengunggah dan mengindeks korpus.",
      "error"
    );
  } finally {
    isIngesting.value = false;
  }
}

async function handleDeleteItem(id: string) {
  try {
    await corpusService.delete(id);
    showNotification(`Koleksi korpus telah berhasil dihapus.`, "info");
    await loadCorpus();
  } catch (err: any) {
    showNotification(
      err?.response?.data?.detail || err?.message || "Gagal menghapus dokumen korpus.",
      "error"
    );
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <!-- Header -->
    <div>
      <h1 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Bank Dokumen Korpus Pembanding
      </h1>
      <p class="text-xs sm:text-sm text-[#777b86] mt-1.5 font-normal">
        Koleksi repositori naskah akademik terindeks <span class="italic font-medium text-[#17191c]">pgvector HNSW (384D)</span> &amp; <span class="italic font-medium text-[#17191c]">Rabin-Karp Winnowing</span> untuk pembandingan leksikal &amp; semantik.
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
