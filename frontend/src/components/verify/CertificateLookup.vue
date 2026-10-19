<script setup lang="ts">
import { ref } from "vue";
import Button from "../common/Button.vue";

const props = withDefaults(
  defineProps<{
    initialValue?: string;
    loading?: boolean;
  }>(),
  {
    initialValue: "",
    loading: false,
  }
);

const emit = defineEmits<{
  (e: "verify", uuid: string): void;
}>();

const inputUuid = ref(props.initialValue);

function handleVerify() {
  if (inputUuid.value.trim()) {
    emit("verify", inputUuid.value.trim());
  }
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-full p-2 pl-4 shadow-[0_0_0_1px_rgba(4,23,43,0.05)] flex flex-col sm:flex-row items-center gap-3">
    <div class="relative flex-grow w-full">
      <input
        v-model="inputUuid"
        type="text"
        placeholder="Masukkan UUID Sertifikat VeriText (contoh: f47ac10b-58cc-4372-a567-0e02b2c3d479)"
        class="w-full px-3 py-2 pl-8 rounded-full border-0 text-xs font-normal text-[#17191c] placeholder:text-[#a3a6af] focus:outline-none bg-transparent tracking-tight"
        @keyup.enter="handleVerify"
      />
      <svg class="w-3.5 h-3.5 absolute left-2.5 top-3 text-[#777b86]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
    <Button
      variant="primary"
      size="sm"
      :loading="loading"
      :disabled="!inputUuid.trim() || loading"
      @click="handleVerify"
      class="w-full sm:w-auto whitespace-nowrap"
    >
      Verifikasi UUID &rarr;
    </Button>
  </div>
</template>
