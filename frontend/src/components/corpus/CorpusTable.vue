<script setup lang="ts">
import Badge from "../common/Badge.vue";
import EmptyState from "../common/EmptyState.vue";
import SkeletonLoader from "../common/SkeletonLoader.vue";

export interface CorpusItemData {
  id: string;
  title: string;
  category?: string | null;
  academic_year?: string | null;
  total_chunks?: number | null;
  status: string;
  created_at: string;
}

interface Props {
  items: CorpusItemData[];
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "deleteItem", id: string): void;
}>();

function getStatusVariant(status: string): "success" | "warning" | "danger" | "neutral" {
  switch (status) {
    case "INDEXED":
      return "success";
    case "INDEXING":
    case "PENDING_INDEX":
      return "warning";
    case "ERROR":
      return "danger";
    default:
      return "neutral";
  }
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle overflow-hidden space-y-4">
    <div class="p-5 border-b border-[#ededed] flex items-center justify-between">
      <h3 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
        Daftar Repositori Naskah Terindeks
      </h3>
      <span class="text-xs text-audyr-ash font-mono">Total: {{ items.length }} dokumen</span>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="p-6">
      <SkeletonLoader shape="table-row" :count="4" />
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="p-8">
      <EmptyState
        icon="📚"
        title="Tidak Ada Dokumen Korpus Ditemukan"
        description="Cobalah sesuaikan kata kunci pencarian atau unggah file arsip korpus baru."
      />
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-white border-y border-[#ededed] text-audyr-ash font-medium uppercase text-[11px] tracking-tight">
            <th class="py-3 px-5">Judul Dokumen / Koleksi</th>
            <th class="py-3 px-4">Kategori Bidang</th>
            <th class="py-3 px-4">Tahun Akademik</th>
            <th class="py-3 px-4">Jumlah Vektor (Chunks)</th>
            <th class="py-3 px-4">Status Indeksasi</th>
            <th class="py-3 px-4">Tanggal Masuk</th>
            <th class="py-3 px-5 text-right">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr v-for="item in items" :key="item.id" class="hover:bg-[#fafafa] transition-colors">
            <td class="py-3.5 px-5 font-semibold text-audyr-ink max-w-xs truncate" :title="item.title">
              {{ item.title }}
            </td>
            <td class="py-3.5 px-4 text-audyr-slate">{{ item.category || '-' }}</td>
            <td class="py-3.5 px-4 font-mono text-audyr-slate">{{ item.academic_year || '-' }}</td>
            <td class="py-3.5 px-4 font-mono font-bold text-audyr-ink">
              {{ item.total_chunks ? item.total_chunks.toLocaleString() : '0' }}
            </td>
            <td class="py-3.5 px-4">
              <Badge :variant="getStatusVariant(item.status)" size="xs" dot :dotPulse="item.status === 'INDEXING'">
                {{ item.status }}
              </Badge>
            </td>
            <td class="py-3.5 px-4 text-audyr-ash font-mono whitespace-nowrap">{{ item.created_at }}</td>
            <td class="py-3.5 px-5 text-right whitespace-nowrap">
              <button
                type="button"
                @click="emit('deleteItem', item.id)"
                class="text-xs text-red-600 hover:text-red-700 font-medium px-2 py-0.5 hover:bg-red-50 rounded-[4px] transition-colors tracking-tight"
                title="Hapus naskah korpus"
              >
                Hapus
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
