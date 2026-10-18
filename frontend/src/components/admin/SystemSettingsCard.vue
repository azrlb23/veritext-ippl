<script setup lang="ts">
import { ref } from "vue";
import Button from "../common/Button.vue";
import type { SystemConfig } from "../../types/admin";

interface Props {
  initialConfig?: SystemConfig;
}

const props = withDefaults(defineProps<Props>(), {
  initialConfig: () => ({
    winnowing_kgram: 5,
    winnowing_window: 4,
    hnsw_similarity_threshold: 0.78,
    hnsw_ef_search: 64,
    stylometric_burstiness_threshold: 0.35,
    sandbox_mode: true,
  }),
});

const emit = defineEmits<{
  (e: "saveConfig", config: SystemConfig): void;
}>();

const config = ref<SystemConfig>({ ...props.initialConfig });
const saved = ref(false);

function handleSave() {
  emit("saveConfig", config.value);
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 2500);
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle p-6 space-y-6">
    <div class="flex items-center justify-between border-b border-[#ededed] pb-4">
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
          Parameter Hyper-Tuning Pipa Hybrid 4-Tier
        </h3>
        <p class="text-xs text-audyr-ash mt-0.5">Konfigurasi algoritma deteksi plagiarisme dan inferensi semantik</p>
      </div>

      <span v-if="saved" class="text-xs font-medium text-[#065f46] bg-audyr-mint-whisper border border-[#a7f3d0] px-3 py-0.5 rounded-full tracking-tight">
        ✓ Konfigurasi Tersimpan
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
      <!-- Winnowing K-gram -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle">
        <label class="font-semibold text-audyr-ink tracking-tight block">Winnowing K-gram (k)</label>
        <p class="text-[11px] text-audyr-ash">Panjang karakter substring fingerprint Rabin-Karp</p>
        <input
          v-model.number="config.winnowing_kgram"
          type="number"
          min="3"
          max="12"
          class="w-full px-3 py-1.5 rounded-[4px] border border-[#ededed] font-mono text-sm text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <!-- Winnowing Window -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle">
        <label class="font-semibold text-audyr-ink tracking-tight block">Sliding Window (w)</label>
        <p class="text-[11px] text-audyr-ash">Jendela seleksi minimum hash leksikal</p>
        <input
          v-model.number="config.winnowing_window"
          type="number"
          min="2"
          max="10"
          class="w-full px-3 py-1.5 rounded-[4px] border border-[#ededed] font-mono text-sm text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <!-- HNSW Threshold -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle">
        <label class="font-semibold text-audyr-ink tracking-tight block">Ambang Kosinus pgvector</label>
        <p class="text-[11px] text-audyr-ash">Nilai kemiripan minimum representasi kalimat</p>
        <input
          v-model.number="config.hnsw_similarity_threshold"
          type="number"
          step="0.01"
          min="0.5"
          max="0.99"
          class="w-full px-3 py-1.5 rounded-[4px] border border-[#ededed] font-mono text-sm text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <!-- HNSW ef_search -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle">
        <label class="font-semibold text-audyr-ink tracking-tight block">HNSW ef_search Index</label>
        <p class="text-[11px] text-audyr-ash">Presisi pencarian graf nearest neighbor</p>
        <input
          v-model.number="config.hnsw_ef_search"
          type="number"
          min="16"
          max="256"
          class="w-full px-3 py-1.5 rounded-[4px] border border-[#ededed] font-mono text-sm text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <!-- Stylometric Burstiness -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle">
        <label class="font-semibold text-audyr-ink tracking-tight block">Threshold Burstiness AI</label>
        <p class="text-[11px] text-audyr-ash">Batas varians deviasi panjang kalimat LLM</p>
        <input
          v-model.number="config.stylometric_burstiness_threshold"
          type="number"
          step="0.01"
          min="0.1"
          max="0.8"
          class="w-full px-3 py-1.5 rounded-[4px] border border-[#ededed] font-mono text-sm text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white"
        />
      </div>

      <!-- Mode Sandbox -->
      <div class="space-y-1.5 p-4 rounded-[8px] bg-white border border-[#ededed] shadow-audyr-subtle flex flex-col justify-between">
        <div>
          <label class="font-semibold text-audyr-ink tracking-tight block">Mode Sandbox IPPL</label>
          <p class="text-[11px] text-audyr-ash">Simulasi Midtrans dan Celery mock worker</p>
        </div>
        <div class="flex items-center space-x-2 pt-2">
          <input
            v-model="config.sandbox_mode"
            type="checkbox"
            id="sandboxMode"
            class="rounded-[2px] text-audyr-ink focus:ring-audyr-ink accent-[#262626] w-4 h-4"
          />
          <label for="sandboxMode" class="font-medium text-audyr-ink">
            {{ config.sandbox_mode ? 'Sandbox Aktif (Mocking)' : 'Production (Live API)' }}
          </label>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-end pt-2">
      <Button
        variant="primary"
        size="sm"
        @click="handleSave"
      >
        Simpan Perubahan Hyperparameter
      </Button>
    </div>
  </div>
</template>
