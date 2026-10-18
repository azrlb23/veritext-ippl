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
  <div class="bg-white border border-[#ededed] rounded-[14px] p-4 shadow-audyr-subtle flex flex-col sm:flex-row items-center gap-3">
    <div class="relative flex-grow w-full">
      <input
        v-model="inputUuid"
        type="text"
        placeholder="Masukkan UUID Sertifikat VeriText (contoh: f47ac10b-58cc-4372-a567-0e02b2c3d479)"
        class="w-full px-3.5 py-2 pl-9 rounded-[4px] border border-[#ededed] text-xs font-mono text-audyr-ink placeholder:text-audyr-fog focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white tracking-tight"
        @keyup.enter="handleVerify"
      />
      <span class="absolute left-3 top-2.5 text-audyr-ash text-xs">🔍</span>
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
