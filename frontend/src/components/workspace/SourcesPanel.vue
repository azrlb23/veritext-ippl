<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { HeatmapAnnotation, MatchedSource } from "../../types";

const PER_PAGE = 10;
const props = defineProps<{ sources: MatchedSource[]; annotations?: HeatmapAnnotation[] }>();
const emit = defineEmits<{ (e: "select-annotation", a: HeatmapAnnotation): void }>();

type FilterKind = "all" | "web" | "corpus";
const filter = ref<FilterKind>("all");
const page = ref(1);
const expanded = ref<Record<string, boolean>>({});
const showAll = ref<Record<string, boolean>>({});

const filteredSources = computed(() => {
  if (filter.value === "web") return props.sources.filter((s) => Boolean(s.source_url));
  if (filter.value === "corpus") return props.sources.filter((s) => !s.source_url);
  return props.sources;
});
watch([() => props.sources, filter], () => { page.value = 1; });

const totalPages = computed(() => Math.max(1, Math.ceil(filteredSources.value.length / PER_PAGE)));
const pagedSources = computed(() => filteredSources.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE));
const pct = (v: number) => (v > 0 && v < 0.1 ? "< 0,1" : Number(v || 0).toFixed(1).replace(".", ","));
const keyOf = (s: MatchedSource, i: number) => `${s.corpus_doc_id || s.title}-${i}`;

function sentencesFor(s: MatchedSource): HeatmapAnnotation[] {
  const list = (props.annotations || []).filter(
    (a) => (a.tier === "T1" || a.tier === "T2") && (a.source_title === s.title || (Boolean(s.source_url) && a.source_url === s.source_url)),
  );
  return [...list].sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
}
function toggleRow(k: string) { expanded.value[k] = !expanded.value[k]; }
</script>

<template>
  <section class="rounded-[32px] border border-[#E8ECEB] bg-white p-6 shadow-float sm:p-8" aria-label="Daftar sumber">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h2 class="text-[18px] font-semibold tracking-[-0.02em] text-[#14111C]">
        Sumber yang mirip <span class="text-[#5E5A6B]">({{ filteredSources.length }})</span>
      </h2>
      <div class="inline-flex rounded-full bg-[#F2F5F4] p-1" role="tablist" aria-label="Filter sumber">
        <button v-for="tab in ([['all', 'Semua'], ['web', 'Jurnal & Web'], ['corpus', 'Korpus Lokal']] as const)" :key="tab[0]" type="button" role="tab" :aria-selected="filter === tab[0]" class="h-9 cursor-pointer rounded-full px-4 text-[13px] font-semibold transition-colors" :class="filter === tab[0] ? 'bg-[#14111C] text-white' : 'text-[#4B4757] hover:text-[#14111C]'" @click="filter = tab[0]">{{ tab[1] }}</button>
      </div>
    </div>

    <p v-if="filteredSources.length === 0" class="mt-4 text-[15px] text-[#5E5A6B]">Tidak ada sumber yang cocok pada kategori ini.</p>
    <template v-else>
      <ul class="mt-3 divide-y divide-[#14111C]/[0.06]">
        <li v-for="(s, i) in pagedSources" :key="keyOf(s, i)" class="py-3.5">
          <div role="button" tabindex="0" class="flex cursor-pointer items-start justify-between gap-4 rounded-xl px-2 py-1.5 transition-colors hover:bg-[#F8FAFC] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]" @click="toggleRow(keyOf(s, i))" @keydown.enter.prevent="toggleRow(keyOf(s, i))">
            <div class="min-w-0">
              <p class="text-[15px] font-semibold leading-snug text-[#14111C]">{{ s.title }}</p>
              <p class="mt-1 text-[13px] text-[#5E5A6B]">
                {{ s.category || "Arsip" }} · {{ sentencesFor(s).length }} kalimat cocok
                <a v-if="s.source_url" :href="s.source_url" target="_blank" rel="noopener noreferrer" class="ml-2 font-medium text-[#0F766E] hover:underline" @click.stop>Buka sumber</a>
              </p>
            </div>
            <div class="flex flex-shrink-0 items-center gap-3">
              <p class="text-[18px] font-semibold tabular-nums text-[#B91C1C]">{{ pct(s.contribution_pct) }}%</p>
              <svg class="h-4 w-4 text-[#5E5A6B] transition-transform" :class="expanded[keyOf(s, i)] ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>
            </div>
          </div>

          <div v-if="expanded[keyOf(s, i)]" class="mt-2.5 space-y-2 border-l-2 border-[#CBE6E1] pl-4">
            <p v-if="sentencesFor(s).length === 0" class="text-[13px] text-[#5E5A6B]">Detail kalimat belum tersedia untuk laporan ini.</p>
            <button v-for="(a, ai) in (showAll[keyOf(s, i)] ? sentencesFor(s) : sentencesFor(s).slice(0, 5))" :key="ai" type="button" class="block w-full cursor-pointer rounded-xl border border-[#E8ECEB] bg-[#F8FAFC] p-3 text-left transition-colors hover:border-[#0F766E] hover:bg-[#EBF8F6]" @click="emit('select-annotation', a)">
              <div class="flex items-baseline justify-between gap-2">
                <span class="text-[12px] font-semibold text-[#0F766E]">{{ a.tier === 'T1' ? 'Kata sama' : 'Makna sama' }}</span>
                <span class="text-[12px] font-semibold tabular-nums text-[#14111C]">{{ ((a.similarity > 1 ? a.similarity : a.similarity * 100)).toFixed(1).replace('.', ',') }}%</span>
              </div>
              <p class="mt-1 line-clamp-2 text-[13.5px] leading-snug text-[#14111C]">{{ a.text_snippet }}</p>
            </button>
            <button v-if="sentencesFor(s).length > 5 && !showAll[keyOf(s, i)]" type="button" class="cursor-pointer text-[13px] font-semibold text-[#0F766E] hover:underline" @click="showAll[keyOf(s, i)] = true">
              Tampilkan semua ({{ sentencesFor(s).length }} kalimat)
            </button>
          </div>
        </li>
      </ul>
      <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between gap-3 border-t border-[#E8ECEB] pt-4">
        <button type="button" :disabled="page <= 1" class="vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] disabled:opacity-40" @click="page--">Sebelumnya</button>
        <p class="text-[14px] font-medium tabular-nums text-[#5E5A6B]">Halaman {{ page }} dari {{ totalPages }}</p>
        <button type="button" :disabled="page >= totalPages" class="vt-btn-light inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium text-[#14111C] disabled:opacity-40" @click="page++">Berikutnya</button>
      </div>
    </template>
  </section>
</template>
