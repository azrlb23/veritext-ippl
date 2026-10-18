<script setup lang="ts">
import Modal from "../common/Modal.vue";
import Badge from "../common/Badge.vue";
import type { HeatmapAnnotation } from "../../types";

interface Props {
  isOpen: boolean;
  annotation: HeatmapAnnotation | null;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: "close"): void;
}>();

function getTierBadgeVariant(tier?: string): "danger" | "warning" | "neutral" {
  if (tier === "T1") return "danger";
  if (tier === "T2") return "warning";
  return "neutral";
}
</script>

<template>
  <Modal
    :isOpen="isOpen"
    title="Rincian Temuan Deteksi Kalimat"
    maxWidth="lg"
    @close="emit('close')"
  >
    <div v-if="annotation" class="space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-[#ededed]">
        <Badge
          :variant="getTierBadgeVariant(annotation.tier)"
          size="md"
        >
          {{ annotation.tier }}: {{ annotation.color }}
        </Badge>

        <div class="text-xs tabular-nums font-bold text-audyr-ink">
          Kemiripan: <span class="font-extrabold text-audyr-ink">{{ (annotation.similarity * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <div class="space-y-1">
        <span class="text-[11px] font-bold text-audyr-ash uppercase tracking-tight">Sumber Pembanding Terdeteksi</span>
        <div class="text-sm font-bold text-audyr-ink">
          {{ annotation.source_title || "Pola Korpus Terdaftar" }}
        </div>
        <div v-if="annotation.source_chunk_id" class="text-xs text-audyr-ash tabular-nums font-medium">
          Chunk ID: {{ annotation.source_chunk_id }}
        </div>
      </div>

      <div class="space-y-1">
        <span class="text-[11px] font-bold text-audyr-ash uppercase tracking-tight">Kutipan Naskah Sumber Terkait</span>
        <div class="p-3.5 bg-white border border-[#ededed] rounded-[8px] text-xs italic font-medium text-audyr-slate leading-relaxed shadow-audyr-subtle">
          "{{ annotation.text_snippet }}"
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 pt-1 text-xs">
        <div class="p-3 bg-white border border-[#ededed] rounded-[8px] shadow-audyr-subtle">
          <span class="text-[10px] text-audyr-ash font-bold uppercase tracking-tight block">Rentang Karakter</span>
          <span class="font-extrabold tabular-nums text-audyr-ink">Offset {{ annotation.start }} - {{ annotation.end }}</span>
        </div>
        <div class="p-3 bg-white border border-[#ededed] rounded-[8px] shadow-audyr-subtle">
          <span class="text-[10px] text-audyr-ash font-bold uppercase tracking-tight block">Metode Deteksi</span>
          <span class="italic font-bold text-audyr-ink">
            {{ annotation.tier === 'T1' ? 'Winnowing Rabin-Karp' : annotation.tier === 'T2' ? 'MiniLM-L12 pgvector' : 'Stilometri Burstiness' }}
          </span>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        @click="emit('close')"
        class="px-4 py-2 bg-transparent hover:bg-[#ededed] text-audyr-ink border border-[#ededed] rounded-[4px] text-xs font-medium transition-colors"
      >
        Tutup
      </button>
    </template>
  </Modal>
</template>
