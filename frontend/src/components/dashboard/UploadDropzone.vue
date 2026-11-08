<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useFileUpload } from "../../composables";
import { useUploadEstimate } from "../../composables/useUploadEstimate";
import AuditSummary from "./AuditSummary.vue";
import DepthChoice from "./DepthChoice.vue";
import DropArea from "./DropArea.vue";

interface Props {
  isUploading?: boolean;
  tokenBalance?: number;
}
const props = withDefaults(defineProps<Props>(), { isUploading: false, tokenBalance: 3 });

const emit = defineEmits<{
  (e: "startAudit", payload: { file: File; depth: "FULL" | "TIER1_ONLY"; cost: number }): void;
  (e: "topup"): void;
}>();

const auditDepth = ref<"FULL" | "TIER1_ONLY">("FULL");
const consentChecked = ref(true);
const dropArea = ref<InstanceType<typeof DropArea> | null>(null);

const { selectedFile, isDragging, error: uploadError, handleFileSelect, handleDragOver, handleDragLeave, handleDrop, reset } = useFileUpload({
  allowedExtensions: [".pdf", ".docx", ".txt"],
  maxSizeBytes: 15 * 1024 * 1024,
});

const { estimate, isEstimating, estimateError, run: runEstimate, clear: clearEstimate } = useUploadEstimate();
watch(selectedFile, (file) => (file ? void runEstimate(file) : clearEstimate()));

const needsConsent = computed(() => auditDepth.value === "FULL");
const isConsentValid = computed(() => !needsConsent.value || consentChecked.value);
const canAfford = computed(() => estimate.value !== null && props.tokenBalance >= estimate.value.token_cost);
const isReady = computed(
  () => Boolean(selectedFile.value) && estimate.value !== null && estimate.value.within_plan && canAfford.value && !props.isUploading && isConsentValid.value
);

function handleFileReset() {
  reset();
  dropArea.value?.clear();
}

function handleStart() {
  if (!isReady.value || !selectedFile.value || !estimate.value) return;
  emit("startAudit", { file: selectedFile.value, depth: auditDepth.value, cost: estimate.value.token_cost });
}

defineExpose({ reset: handleFileReset, triggerFilePicker: () => dropArea.value?.pick() });
</script>

<template>
  <div class="grid items-start gap-6 font-sans lg:grid-cols-12 lg:gap-8">
    <div class="space-y-6 lg:col-span-7">
      <div class="rounded-[36px] bg-white p-3 shadow-float">
        <DropArea
          ref="dropArea"
          :file="selectedFile"
          :is-dragging="isDragging"
          :error="uploadError || ''"
          @select="handleFileSelect"
          @reset="reset"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        />
      </div>
      <DepthChoice v-model="auditDepth" />
    </div>

    <div class="lg:col-span-5">
      <AuditSummary
        v-model:consent="consentChecked"
        :balance="tokenBalance"
        :estimate="estimate"
        :is-estimating="isEstimating"
        :estimate-error="estimateError"
        :file-name="selectedFile ? selectedFile.name : ''"
        :needs-consent="needsConsent"
        :is-ready="isReady"
        :is-uploading="isUploading"
        @start="handleStart"
        @topup="emit('topup')"
      />
    </div>
  </div>
</template>
