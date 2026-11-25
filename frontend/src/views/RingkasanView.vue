<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import ActiveAudits from "../components/ringkasan/ActiveAudits.vue";
import SummaryCards from "../components/ringkasan/SummaryCards.vue";
import RiwayatRow from "../components/riwayat/RiwayatRow.vue";
import { useSectionReveal } from "../composables";
import { useAuditTasks } from "../composables/useAuditTasks";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { tasks, loading, activeTasks, doneTasks, cancel } = useAuditTasks();

const firstName = computed(() => (authStore.user?.full_name || "").split(" ")[0] || "Anda");
const recent = computed(() => doneTasks.value.slice(0, 3));
const average = computed(() => {
  const scores = doneTasks.value.map((t) => t.score).filter((s): s is number => s !== null);
  return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
});
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-5 max-w-4xl">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Halo {{ firstName }}, siap menulis lebih orisinal?
      </h1>
    </div>

    <div class="space-y-8">
      <SummaryCards :balance="authStore.tokenBalance" :total="tasks.length" :done="doneTasks.length" :average="average" :role="authStore.role" />
      <ActiveAudits :tasks="activeTasks" />

      <section class="vt-reveal vt-d-2 pt-1" aria-labelledby="terakhir-judul">
        <div class="flex items-center justify-between gap-4">
          <h2 id="terakhir-judul" class="text-[19px] font-semibold tracking-[-0.025em] text-[#14111C]">Terakhir diperiksa</h2>
          <router-link to="/riwayat" class="inline-flex h-9 cursor-pointer items-center rounded-full px-3 text-[13.5px] font-semibold text-[#0F766E] transition-colors hover:bg-[#EBF8F6] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]">Lihat semua</router-link>
        </div>
        <p v-if="!loading && recent.length === 0" class="py-10 text-center text-[14.5px] text-[#5E5A6B]">Belum ada hasil. Mulai dengan mengunggah naskah pertama Anda.</p>
        <ul v-else class="mt-2 divide-y divide-[#E6ECEB]">
          <RiwayatRow v-for="t in recent" :key="t.id" :task="t" :allow-delete="false" @open="(id) => router.push(`/audits/${id}`)" @cancel="cancel" />
        </ul>
      </section>
    </div>
  </div>
</template>
