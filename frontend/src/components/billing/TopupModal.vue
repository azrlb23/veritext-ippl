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
    <div v-if="selectedPackage" class="space-y-5 font-sans">
      <!-- Order Summary Card -->
      <div class="bg-[#F8FAFC] border border-[#E4E8F0] rounded-[20px] p-5 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-[#5B6475]">Paket Terpilih</span>
          <span class="font-bold text-[#0B0F19]">{{ selectedPackage.name }}</span>
        </div>
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-[#5B6475]">Jumlah Kuota</span>
          <span class="font-bold text-[#0B0F19] tabular-nums">{{ selectedPackage.tokens }} Token</span>
        </div>
        <div class="border-t border-[#E4E8F0] pt-2.5 flex items-center justify-between">
          <span class="text-xs font-bold text-[#0B0F19]">Total Pembayaran</span>
          <span class="text-base font-extrabold text-[#1560BD] tabular-nums">{{ selectedPackage.price }}</span>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div class="space-y-2.5">
        <label class="block text-xs font-bold uppercase tracking-wider text-[#5B6475]">
          PILIH JALUR PEMBAYARAN (MIDTRANS)
        </label>

        <div class="grid grid-cols-1 gap-2.5">
          <label
            class="flex items-center justify-between p-3.5 rounded-[16px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'qris' ? 'border-[#1560BD] bg-[#EAF3FE]/40 ring-1 ring-[#1560BD]' : 'border-[#E4E8F0] hover:border-[#CBD5E1] bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="qris"
                v-model="selectedPaymentMethod"
                class="text-[#1560BD] focus:ring-[#1560BD] accent-[#1560BD]"
              />
              <span class="font-bold text-[#0B0F19]">QRIS (GoPay, OVO, ShopeePay, DANA)</span>
            </div>
            <span class="text-[10px] bg-[#EAF7EE] text-[#15803D] border border-[#A7F3D0] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-tight">Instan</span>
          </label>

          <label
            class="flex items-center justify-between p-3.5 rounded-[16px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'va_bca' ? 'border-[#1560BD] bg-[#EAF3FE]/40 ring-1 ring-[#1560BD]' : 'border-[#E4E8F0] hover:border-[#CBD5E1] bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="va_bca"
                v-model="selectedPaymentMethod"
                class="text-[#1560BD] focus:ring-[#1560BD] accent-[#1560BD]"
              />
              <span class="font-bold text-[#0B0F19]">BCA Virtual Account</span>
            </div>
            <span class="text-[10px] text-[#5B6475] font-semibold">Otomatis</span>
          </label>

          <label
            class="flex items-center justify-between p-3.5 rounded-[16px] border cursor-pointer transition-all text-xs"
            :class="selectedPaymentMethod === 'va_mandiri' ? 'border-[#1560BD] bg-[#EAF3FE]/40 ring-1 ring-[#1560BD]' : 'border-[#E4E8F0] hover:border-[#CBD5E1] bg-white'"
          >
            <div class="flex items-center space-x-3">
              <input
                type="radio"
                value="va_mandiri"
                v-model="selectedPaymentMethod"
                class="text-[#1560BD] focus:ring-[#1560BD] accent-[#1560BD]"
              />
              <span class="font-bold text-[#0B0F19]">Mandiri / BRI / BNI VA</span>
            </div>
            <span class="text-[10px] text-[#5B6475] font-semibold">Otomatis</span>
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
