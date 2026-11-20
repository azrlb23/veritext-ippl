<script setup lang="ts">
import type { HeatmapAnnotation, MatchedSource } from "../../types";

defineProps<{ selected?: HeatmapAnnotation | null; sources: MatchedSource[] }>();
defineEmits<{ (e: "rewrite", a: HeatmapAnnotation): void }>();
const pct = (v: number) => (v > 1 ? v : v * 100).toFixed(1).replace(".", ",");
</script>

<template>
  <div class="space-y-5">
    <section class="rounded-[28px] border border-[#D5ECE8] bg-[#EBF8F6] p-6" aria-label="Kalimat terpilih">
      <template v-if="selected">
        <p class="text-[13px] font-medium text-[#5E5A6B]">Kalimat di naskah Anda</p>
        <p class="mt-1 text-[16px] leading-relaxed text-[#14111C]">{{ selected.text_snippet || "Kalimat terpilih" }}</p>
        <p class="mt-5 text-[13px] font-medium text-[#5E5A6B]">Mirip dengan <span v-if="selected.source_title" class="text-[#14111C]">{{ selected.source_title }}</span></p>
        <p class="mt-1 text-[15px] leading-relaxed text-[#4B4757]">{{ selected.reason || "Ditemukan kemiripan dengan sumber pembanding." }}</p>
        <div class="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-[32px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[#14111C]">{{ pct(selected.similarity ?? 0) }}%<span class="ml-2 text-[14px] font-medium tracking-normal text-[#5E5A6B]">mirip</span></p>
          <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2" @click="$emit('rewrite', selected)">Tulis ulang kalimat ini</button>
        </div>
      </template>
      <p v-else class="py-6 text-center text-[15px] text-[#5E5A6B]">Pilih kalimat yang tersorot di naskah untuk melihat pembandingnya.</p>
    </section>

    <section aria-label="Daftar sumber">
      <h3 class="text-[18px] font-semibold tracking-[-0.02em] text-[#14111C]">Sumber yang mirip <span class="text-[#5E5A6B]">({{ sources.length }})</span></h3>
      <p v-if="sources.length === 0" class="mt-3 text-[15px] text-[#5E5A6B]">Tidak ada sumber yang cocok.</p>
      <ul v-else class="mt-2 divide-y divide-[#14111C]/[0.06]">
        <li v-for="(s, i) in sources" :key="i" class="flex items-start justify-between gap-4 py-4">
          <div class="min-w-0">
            <p class="text-[15px] font-semibold leading-snug text-[#14111C]">{{ s.title }}</p>
            <p class="mt-1 text-[13px] text-[#5E5A6B]">{{ s.category || "Arsip" }}
              <a v-if="s.source_url" :href="s.source_url" target="_blank" rel="noopener noreferrer" class="ml-2 inline-flex min-h-[44px] items-center font-medium text-[#0F766E] hover:underline">Buka sumber</a>
            </p>
          </div>
          <p class="flex-shrink-0 text-[18px] font-semibold tabular-nums text-[#B91C1C]">{{ pct(s.contribution_pct) }}%</p>
        </li>
      </ul>
    </section>
  </div>
</template>
