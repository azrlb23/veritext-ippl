<script setup lang="ts">
import type { MatchedSource } from "../../types";
import EmptyState from "../common/EmptyState.vue";

interface Props {
  sources: MatchedSource[];
}

withDefaults(defineProps<Props>(), {
  sources: () => [],
});
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle overflow-hidden p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
        Daftar Sumber Dokumen Pembanding yang Cocok
      </h3>
      <span class="text-xs text-audyr-ash font-mono">Total: {{ sources.length }} rujukan</span>
    </div>

    <div v-if="sources.length === 0" class="py-6">
      <EmptyState
        icon="📄"
        title="Tidak Ditemukan Sumber Pembanding"
        description="Naskah ini tidak memiliki kecocokan signifikan dengan bank korpus yang terdaftar."
      />
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-white border-y border-[#ededed] text-audyr-ash font-medium uppercase text-[11px] tracking-tight">
            <th class="py-3 px-4">Judul Dokumen Sumber</th>
            <th class="py-3 px-4">Kategori Bidang</th>
            <th class="py-3 px-4 text-right">Kontribusi Kemiripan</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr v-for="source in sources" :key="source.corpus_doc_id" class="hover:bg-[#fafafa] transition-colors">
            <td class="py-3 px-4 font-medium text-audyr-ink">
              <div class="flex items-center space-x-2">
                <span class="w-1.5 h-1.5 rounded-full bg-audyr-ink"></span>
                <span>{{ source.title }}</span>
              </div>
            </td>
            <td class="py-3 px-4 text-audyr-ash">{{ source.category || '-' }}</td>
            <td class="py-3 px-4 text-right font-mono font-bold text-audyr-ink">
              {{ source.contribution_pct.toFixed(1) }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
