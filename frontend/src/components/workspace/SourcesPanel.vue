<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { MatchedSource } from "../../types";

const PER_PAGE = 10;
const props = defineProps<{ sources: MatchedSource[] }>();
const page = ref(1);
watch(() => props.sources, () => { page.value = 1; });
const totalPages = computed(() => Math.max(1, Math.ceil(props.sources.length / PER_PAGE)));
const pagedSources = computed(() => props.sources.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE));
const pct = (v: number) => (v > 0 && v < 0.1 ? "< 0,1" : Number(v || 0).toFixed(1).replace(".", ","));
</script>

<template>
  <section class="rounded-[32px] border border-[#E8ECEB] bg-white p-6 shadow-float sm:p-8" aria-label="Daftar sumber">
    <h2 class="text-[18px] font-semibold tracking-[-0.02em] text-[#14111C]">
      Sumber yang mirip <span class="text-[#5E5A6B]">({{ sources.length }})</span>
    </h2>
    <p v-if="sources.length === 0" class="mt-3 text-[15px] text-[#5E5A6B]">Tidak ada sumber yang cocok.</p>
    <template v-else>
      <ul class="mt-3 divide-y divide-[#14111C]/[0.06]">
        <li v-for="(s, i) in pagedSources" :key="`${page}-${i}`" class="flex items-start justify-between gap-4 py-4">
          <div class="min-w-0">
            <p class="text-[15px] font-semibold leading-snug text-[#14111C]">{{ s.title }}</p>
            <p class="mt-1 text-[13px] text-[#5E5A6B]">
              {{ s.category || "Arsip" }}
              <a
                v-if="s.source_url"
                :href="s.source_url"
                target="_blank"
                rel="noopener noreferrer"
                class="ml-2 inline-flex min-h-[44px] items-center font-medium text-[#0F766E] hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
              >Buka sumber</a>
            </p>
          </div>
          <p class="flex-shrink-0 text-[18px] font-semibold tabular-nums text-[#B91C1C]">{{ pct(s.contribution_pct) }}%</p>
        </li>
      </ul>
      <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between gap-3 border-t border-[#E8ECEB] pt-4">
        <button type="button" :disabled="page <= 1" class="vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-40" @click="page--">Sebelumnya</button>
        <p class="text-[14px] font-medium tabular-nums text-[#5E5A6B]">Halaman {{ page }} dari {{ totalPages }}</p>
        <button type="button" :disabled="page >= totalPages" class="vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-40" @click="page++">Berikutnya</button>
      </div>
    </template>
  </section>
</template>
