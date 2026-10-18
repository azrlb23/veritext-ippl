<script setup lang="ts">
import { ref } from "vue";
import Modal from "../common/Modal.vue";
import Button from "../common/Button.vue";
import type { PlanItem } from "./PlanCard.vue";

interface Props {
  isOpen: boolean;
  selectedPackage: PlanItem | null;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "close"): void;
  (e: "confirm", payload: { packageId: string; paymentMethod: string }): void;
}>();

const selectedPaymentMethod = ref("qris");

function handleConfirm() {
  if (!props.selectedPackage) return;
  emit("confirm", {
    packageId: props.selectedPackage.id,
    paymentMethod: selectedPaymentMethod.value,
  });
}
</script>

<template>
  <Modal
    :isOpen="isOpen"
    title="Konfirmasi Pembelian Kuota Token"
    maxWidth="md"
    @close="emit('close')"
  >
    <div v-if="selectedPackage" class="space-y-5">
      <!-- Order Summary Card -->
      <div class="bg-white border border-[#ededed] rounded-[14px] p-4 space-y-2.5 shadow-audyr-subtle">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-audyr-ash">Paket Terpilih</span>
          <span class="text-xs font-extrabold text-audyr-ink">{{ selectedPackage.name }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-audyr-ash">Jumlah Kuota</span>
          <span class="text-sm font-extrabold text-audyr-ink tabular-nums">{{ selectedPackage.tokens }} Token</span>
        </div>
        <div class="border-t border-[#ededed] pt-2 flex items-center justify-between">
          <span class="text-xs font-bold text-audyr-ink">Total Pembayaran</span>
          <span class="text-base font-extrabold text-audyr-ink tabular-nums">{{ selectedPackage.price }}</span>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div class="space-y-2">
        <label class="block text-xs font-extrabold uppercase tracking-tight text-audyr-ash">
          Pilih Jalur Pembayaran (Midtrans Payment Gateway)
        </label>

        <div class="grid grid-cols-1 gap-2">
          <label
            class="flex items-center justify-between p-3 rounded-[8px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'qris' ? 'border-audyr-ink bg-white ring-1 ring-audyr-ink' : 'border-[#ededed] hover:border-audyr-ink bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="qris"
                v-model="selectedPaymentMethod"
                class="text-audyr-ink focus:ring-audyr-ink accent-[#262626]"
              />
              <span class="font-bold text-audyr-ink">QRIS (GoPay, OVO, ShopeePay, DANA)</span>
            </div>
            <span class="text-[10px] bg-audyr-mint-whisper text-[#065f46] border border-[#a7f3d0] px-2.5 py-0.5 rounded-full italic font-bold uppercase tracking-tight">Instan</span>
          </label>

          <label
            class="flex items-center justify-between p-3 rounded-[8px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'va_bca' ? 'border-audyr-ink bg-white ring-1 ring-audyr-ink' : 'border-[#ededed] hover:border-audyr-ink bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="va_bca"
                v-model="selectedPaymentMethod"
                class="text-audyr-ink focus:ring-audyr-ink accent-[#262626]"
              />
              <span class="font-bold text-audyr-ink">BCA Virtual Account</span>
            </div>
            <span class="text-[10px] text-audyr-ash font-medium">Otomatis</span>
          </label>

          <label
            class="flex items-center justify-between p-3 rounded-[8px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'va_mandiri' ? 'border-audyr-ink bg-white ring-1 ring-audyr-ink' : 'border-[#ededed] hover:border-audyr-ink bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="va_mandiri"
                v-model="selectedPaymentMethod"
                class="text-audyr-ink focus:ring-audyr-ink accent-[#262626]"
              />
              <span class="font-bold text-audyr-ink">Mandiri / BRI / BNI VA</span>
            </div>
            <span class="text-[10px] text-audyr-ash font-medium">Otomatis</span>
          </label>
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        variant="ghost"
        size="sm"
        @click="emit('close')"
      >
        Batal
      </Button>
      <Button
        variant="primary"
        size="sm"
        :loading="loading"
        @click="handleConfirm"
      >
        Lanjutkan ke Midtrans Snap &rarr;
      </Button>
    </template>
  </Modal>
</template>
