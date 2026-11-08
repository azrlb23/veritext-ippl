<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import ActiveAudits from "../components/ringkasan/ActiveAudits.vue";
import SummaryCards from "../components/ringkasan/SummaryCards.vue";
import RiwayatRow from "../components/riwayat/RiwayatRow.vue";
import { useAuditTasks } from "../composables/useAuditTasks";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const { tasks, loading, activeTasks, doneTasks, cancel } = useAuditTasks();

const firstName = computed(() => (authStore.user?.full_name || "").split(" ")[0] || "Anda");
const recent = computed(() => doneTasks.value.slice(0, 3));
const average = computed(() => {
  const scores = doneTasks.value.map((t) => t.score).filter((s): s is number => s !== null);
  return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
});
</script>

<template>
  <div class="mx-auto max-w-[1180px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-9 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Ringkasan</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Halo {{ firstName }}, <span class="vt-accent">siap menulis lebih orisinal?</span>
      </h1>
    </div>

    <div class="space-y-6">
      <SummaryCards :balance="authStore.tokenBalance" :total="tasks.length" :done="doneTasks.length" :average="average" />
      <ActiveAudits :tasks="activeTasks" />

      <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="terakhir-judul">
        <div class="flex items-center justify-between gap-4">
          <h2 id="terakhir-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Terakhir diperiksa</h2>
          <router-link to="/riwayat" class="inline-flex h-11 cursor-pointer items-center rounded-full px-4 text-[14px] font-semibold text-[#6D28D9] transition-colors hover:bg-[#F3EEFA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]">Lihat semua</router-link>
        </div>
        <p v-if="!loading && recent.length === 0" class="py-10 text-center text-[15px] text-[#5E5A6B]">Belum ada hasil. Mulai dengan mengunggah naskah pertama Anda.</p>
        <ul v-else class="mt-2 divide-y divide-[#14111C]/[0.06]">
          <RiwayatRow v-for="t in recent" :key="t.id" :task="t" @open="(id) => router.push(`/audits/${id}`)" @cancel="cancel" />
        </ul>
      </section>
    </div>
  </div>
</template>
