<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import RiwayatFilters, { type RiwayatFilter } from "../components/riwayat/RiwayatFilters.vue";
import RiwayatRow from "../components/riwayat/RiwayatRow.vue";
import { isActiveStatus, isFailedStatus, useAuditTasks } from "../composables/useAuditTasks";

const router = useRouter();
const { tasks, loading, cancel } = useAuditTasks();
const filter = ref<RiwayatFilter>("ALL");
const query = ref("");
const pendingCancel = ref<string | null>(null);

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
</script>

<template>
  <div class="mx-auto max-w-[1040px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-9 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Riwayat</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Semua pemeriksaan, <span class="vt-accent">satu tempat.</span>
      </h1>
    </div>

    <section class="rounded-[32px] bg-white p-5 shadow-float sm:p-8" aria-label="Daftar pemeriksaan">
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
          class="mt-6 inline-flex h-12 cursor-pointer items-center rounded-full bg-[#14111C] px-7 text-[15px] font-semibold text-white shadow-btn-dark focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2"
        >Periksa naskah</router-link>
      </div>
      <ul v-else class="mt-4 divide-y divide-[#14111C]/[0.06]">
        <RiwayatRow v-for="t in shown" :key="t.id" :task="t" @open="(id) => router.push(`/audits/${id}`)" @cancel="(id) => (pendingCancel = id)" />
      </ul>
    </section>

    <div v-if="pendingCancel" class="fixed inset-0 z-[60] flex items-end justify-center bg-[#14111C]/20 p-4 backdrop-blur-[2px] sm:items-center" @click.self="pendingCancel = null">
      <div class="w-full max-w-md rounded-[32px] bg-white p-7 shadow-float" role="dialog" aria-modal="true" aria-labelledby="batal-judul">
        <h2 id="batal-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Batalkan pemeriksaan?</h2>
        <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">Pemeriksaan dihentikan dan token Anda dikembalikan.</p>
        <div class="mt-7 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button type="button" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#F3EEFA] px-6 text-[15px] font-semibold text-[#14111C]" @click="pendingCancel = null">Kembali</button>
          <button type="button" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark" @click="confirmCancel">Ya, batalkan</button>
        </div>
      </div>
    </div>
  </div>
</template>
