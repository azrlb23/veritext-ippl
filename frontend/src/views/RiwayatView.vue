<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import RiwayatFilters, { type RiwayatFilter } from "../components/riwayat/RiwayatFilters.vue";
import RiwayatRow from "../components/riwayat/RiwayatRow.vue";
import { isActiveStatus, isFailedStatus, useAuditTasks } from "../composables/useAuditTasks";

const router = useRouter();
const { tasks, loading, page, pages, total, changePage, cancel, removeDocument, exportCsv } = useAuditTasks();
const filter = ref<RiwayatFilter>("ALL");
const query = ref("");
const pendingCancel = ref<string | null>(null);
const pendingDelete = ref<string | null>(null);
const navBtn = "vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-40";

const shown = computed(() => {
  const q = query.value.trim().toLowerCase();
  return tasks.value.filter((t) => {
    if (q && !t.title.toLowerCase().includes(q)) return false;
    if (filter.value === "SUCCESS") return t.status === "SUCCESS";
    if (filter.value === "ACTIVE") return isActiveStatus(t.status);
    if (filter.value === "FAILED") return isFailedStatus(t.status);
    return true;
  });
});

async function confirmCancel() {
  const id = pendingCancel.value;
  pendingCancel.value = null;
  if (id) await cancel(id);
}

async function confirmDelete() {
  const docId = pendingDelete.value;
  pendingDelete.value = null;
  if (docId) await removeDocument(docId);
}
</script>

<template>
  <div class="mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="max-w-4xl">
        <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
          Semua pemeriksaan, satu tempat.
        </h1>
      </div>
      <button
        type="button"
        :disabled="tasks.length === 0"
        class="vt-btn-light inline-flex h-11 shrink-0 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-40"
        @click="exportCsv"
      >Unduh CSV</button>
    </div>

    <section class="rounded-[32px] border border-[#E8ECEB] bg-white p-5 shadow-float sm:p-8" aria-label="Daftar pemeriksaan">
      <RiwayatFilters v-model:filter="filter" v-model:query="query" />

      <p v-if="loading" class="py-16 text-center text-[15px] text-[#5E5A6B]">Memuat riwayat...</p>
      <div v-else-if="shown.length === 0" class="py-16 text-center">
        <p class="text-[18px] font-semibold text-[#14111C]">{{ tasks.length === 0 ? "Belum ada pemeriksaan" : "Tidak ada yang cocok" }}</p>
        <p class="mx-auto mt-2 max-w-sm text-[15px] text-[#5E5A6B]">
          {{ tasks.length === 0 ? "Unggah naskah pertama Anda dan hasilnya akan muncul di sini." : "Ubah kata kunci atau pilihan status." }}
        </p>
        <router-link
          v-if="tasks.length === 0"
          to="/periksa"
          class="vt-btn-dark mt-6 inline-flex h-12 cursor-pointer items-center rounded-full px-7 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
        >Periksa naskah</router-link>
      </div>
      <ul v-else class="mt-4 divide-y divide-[#14111C]/[0.06]">
        <RiwayatRow v-for="t in shown" :key="t.id" :task="t" @open="(id) => router.push(`/audits/${id}`)" @cancel="(id) => (pendingCancel = id)" @delete="(docId) => (pendingDelete = docId)" />
      </ul>

      <div v-if="pages > 1" class="mt-6 flex items-center justify-between gap-3 border-t border-[#14111C]/[0.06] pt-5">
        <button type="button" :class="navBtn" :disabled="page <= 1" @click="changePage(page - 1)">Sebelumnya</button>
        <span class="text-[14px] tabular-nums text-[#5E5A6B]">Halaman {{ page }} dari {{ pages }} ({{ total }} total)</span>
        <button type="button" :class="navBtn" :disabled="page >= pages" @click="changePage(page + 1)">Berikutnya</button>
      </div>
    </section>

    <div v-if="pendingCancel" class="fixed inset-0 z-[60] flex items-end justify-center bg-[#14111C]/20 p-4 backdrop-blur-[2px] sm:items-center" @click.self="pendingCancel = null">
      <div class="w-full max-w-md rounded-[32px] bg-white p-7 shadow-float" role="dialog" aria-modal="true" aria-labelledby="batal-judul">
        <h2 id="batal-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Batalkan pemeriksaan?</h2>
        <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">Pemeriksaan dihentikan dan token Anda dikembalikan.</p>
        <div class="mt-7 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button type="button" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="pendingCancel = null">Kembali</button>
          <button type="button" class="vt-btn-dark inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold" @click="confirmCancel">Ya, batalkan</button>
        </div>
      </div>
    </div>

    <div v-if="pendingDelete" class="fixed inset-0 z-[60] flex items-end justify-center bg-[#14111C]/20 p-4 backdrop-blur-[2px] sm:items-center" @click.self="pendingDelete = null">
      <div class="w-full max-w-md rounded-[32px] bg-white p-7 shadow-float" role="dialog" aria-modal="true" aria-labelledby="hapus-judul">
        <h2 id="hapus-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Hapus naskah permanen?</h2>
        <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">Berkas naskah, laporan audit, dan riwayat percakapan terkait akan dihapus permanen dan tidak dapat dipulihkan.</p>
        <div class="mt-7 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button type="button" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="pendingDelete = null">Kembali</button>
          <button type="button" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#B91C1C] px-6 text-[15px] font-semibold text-white" @click="confirmDelete">Ya, hapus permanen</button>
        </div>
      </div>
    </div>
  </div>
</template>
