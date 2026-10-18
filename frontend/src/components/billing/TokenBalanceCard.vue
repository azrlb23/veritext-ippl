<script setup lang="ts">
interface Props {
  balance: number;
}

defineProps<Props>();

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="bg-audyr-charcoal text-white rounded-[14px] border border-neutral-800 p-8 shadow-audyr-subtle flex flex-col md:flex-row md:items-center justify-between gap-6">
    <div class="space-y-2">
      <span class="text-xs uppercase tracking-tight text-audyr-chalk font-medium">Dompet Saldo Token Audit</span>
      <div class="flex items-baseline space-x-3">
        <span class="text-4xl sm:text-5xl font-bold font-mono tracking-tight text-white">{{ balance }}</span>
        <span class="text-sm text-audyr-chalk font-normal">Token Tersedia</span>
      </div>
      <p class="text-xs text-audyr-fog max-w-md leading-relaxed">
        1 Token = 1x Audit Leksikal (Tier 1) &bull; 2 Token = 1x Audit Hybrid Lengkap (Tier 1 - 4 + Sertifikat QR).
      </p>
    </div>

    <div class="bg-audyr-ink border border-neutral-700/60 p-4 rounded-[8px] text-xs space-y-2 self-start md:self-auto">
      <div class="font-medium text-white">Metode Pembayaran Resmi</div>
      <div class="text-audyr-chalk text-[11px]">Midtrans Payment Gateway (QRIS, VA Bank, E-Wallet)</div>
      <div class="flex items-center justify-between gap-4 pt-1">
        <span class="text-[10px] text-audyr-fog font-mono">Status: Sandbox Mode</span>
        <button
          type="button"
          @click="$emit('topup')"
          class="px-3 py-1.5 bg-white text-audyr-ink rounded-[4px] font-medium text-xs hover:bg-[#ededed] transition-colors shadow-audyr-button"
        >
          Top Up Cepat
        </button>
      </div>
    </div>
  </div>
</template>
