<script setup lang="ts">
defineProps<{
  optionId: number;
  style: string;
  text: string;
  predictedScore: number;
  isApplying?: boolean;
}>();

const emit = defineEmits<{
  (e: "apply", text: string): void;
}>();
</script>

<template>
  <div class="p-4 bg-white border border-[#E4E8F0] hover:border-[#1560BD] rounded-xl shadow-xs transition-all space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-1.5">
        <span class="w-5 h-5 rounded-full bg-blue-50 text-[#1560BD] text-[10px] font-bold flex items-center justify-center">
          {{ optionId }}
        </span>
        <span class="text-xs font-semibold text-gray-800">{{ style }}</span>
      </div>
      <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
        Prediksi: {{ (predictedScore * 100).toFixed(0) }}%
      </span>
    </div>

    <p class="text-xs text-gray-700 leading-relaxed font-serif bg-gray-50/60 p-2.5 rounded-lg border border-gray-100">
      "{{ text }}"
    </p>

    <div class="flex justify-end">
      <button
        type="button"
        @click="emit('apply', text)"
        :disabled="isApplying"
        class="px-3 py-1.5 bg-[#1560BD] hover:bg-[#1A73D9] text-white text-xs font-medium rounded-lg shadow-xs transition-all disabled:opacity-50"
      >
        <span v-if="isApplying">Menerapkan...</span>
        <span v-else>Gunakan Kalimat Ini</span>
      </button>
    </div>
  </div>
</template>
