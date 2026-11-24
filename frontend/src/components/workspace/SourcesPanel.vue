<script setup lang="ts">
import type { MatchedSource } from "../../types";

defineProps<{ sources: MatchedSource[] }>();
const pct = (v: number) => (v > 1 ? v : v * 100).toFixed(1).replace(".", ",");
</script>

<template>
  <section class="rounded-[32px] border border-[#E8ECEB] bg-white p-6 shadow-float sm:p-8" aria-label="Daftar sumber">
    <h2 class="text-[18px] font-semibold tracking-[-0.02em] text-[#14111C]">
      Sumber yang mirip <span class="text-[#5E5A6B]">({{ sources.length }})</span>
    </h2>
    <p v-if="sources.length === 0" class="mt-3 text-[15px] text-[#5E5A6B]">Tidak ada sumber yang cocok.</p>
    <ul v-else class="mt-3 divide-y divide-[#14111C]/[0.06]">
      <li v-for="(s, i) in sources" :key="i" class="flex items-start justify-between gap-4 py-4">
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
  </section>
</template>
