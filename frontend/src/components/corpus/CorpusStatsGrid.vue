<script setup lang="ts">
import StatCard from "../common/StatCard.vue";

interface Props {
  totalDocs: number;
  totalChunks: number;
  indexStatus?: string;
}

withDefaults(defineProps<Props>(), {
  totalDocs: 0,
  totalChunks: 0,
  indexStatus: "Aktif & Sinkron",
});
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <StatCard
      title="Total Dokumen Korpus"
      :value="`${totalDocs} Berkas`"
      subtitle="Arsip naskah akademik terdaftar"
      icon="📚"
      variant="primary"
    />

    <StatCard
      title="Vektor Kalimat Terindeks (HNSW)"
      :value="`${totalChunks.toLocaleString()} Kalimat`"
      subtitle="Representasi 384D pgvector"
      icon="🧬"
      variant="default"
    />

    <div class="bg-white p-5 rounded-[14px] border border-[#ededed] shadow-audyr-subtle space-y-1">
      <span class="text-[11px] font-bold text-audyr-ash uppercase tracking-tight">
        Status Indeks pgvector
      </span>
      <div class="text-2xl font-extrabold text-audyr-ink flex items-center space-x-2 pt-1 tracking-tight">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>{{ indexStatus }}</span>
      </div>
      <p class="text-xs text-audyr-ash mt-1"><span class="italic font-bold text-audyr-ink">HNSW cosine distance</span> index siap query</p>
    </div>
  </div>
</template>
