<script setup lang="ts">
import type { DocumentItem } from "../../types";

const props = defineProps<{ documents: DocumentItem[]; modelValue: string[] }>();
const emit = defineEmits<{ (e: "update:modelValue", v: string[]): void }>();
const MAX = 3;

function toggle(id: string) {
  const on = props.modelValue.includes(id);
  if (on) return emit("update:modelValue", props.modelValue.filter((x) => x !== id));
  if (props.modelValue.length < MAX) emit("update:modelValue", [...props.modelValue, id]);
}
</script>

<template>
  <div>
    <p class="text-[14px] font-medium text-[#14111C]">Sertakan naskah <span class="text-[#5E5A6B]">(opsional, maksimal {{ MAX }})</span></p>
    <p v-if="documents.length === 0" class="mt-2 text-[14px] text-[#5E5A6B]">Belum ada naskah. Unggah di halaman Periksa naskah agar asisten bisa membacanya.</p>
    <div v-else class="mt-3 flex flex-wrap gap-2">
      <button
        v-for="d in documents"
        :key="d.id"
        type="button"
        :aria-pressed="modelValue.includes(d.id)"
        class="inline-flex h-11 max-w-full cursor-pointer items-center rounded-full px-5 text-[14px] font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        :class="modelValue.includes(d.id) ? 'bg-[#14111C] text-white shadow-btn-dark' : 'bg-white text-[#14111C] shadow-lift hover:-translate-y-0.5'"
        @click="toggle(d.id)"
      ><span class="truncate">{{ d.original_filename }}</span></button>
    </div>
  </div>
</template>
