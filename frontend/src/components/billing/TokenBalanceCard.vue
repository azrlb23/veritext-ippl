<script setup lang="ts">
interface Props {
  balance: number;
  role?: string;
}

withDefaults(defineProps<Props>(), {
  role: "TRIAL",
});

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="bg-[#17191c] text-white rounded-[24px] border border-neutral-800 p-8 shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_25px_-5px_rgba(0,0,0,0.1)] flex flex-col md:flex-row md:items-center justify-between gap-6">
    <div class="space-y-2">
      <div class="flex items-center space-x-2">
        <span class="text-xs uppercase tracking-wider text-[#a3a6af] font-medium">Dompet Saldo Token Audit</span>
        <span
          v-if="role === 'PREMIUM'"
          class="px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wider bg-white text-[#17191c] uppercase"
        >
          PREMIUM
        </span>
        <span
          v-else
          class="px-2.5 py-0.5 rounded-full text-[10px] font-medium tracking-wider bg-neutral-800 text-[#a3a6af] uppercase"
        >
          TRIAL
        </span>
      </div>
      <div class="flex items-baseline space-x-3">
        <span class="text-4xl sm:text-5xl font-semibold tracking-tight text-white tabular-nums">{{ balance }}</span>
        <span class="text-sm text-[#a3a6af] font-normal">Token Tersedia</span>
      </div>
      <p class="text-xs text-[#a3a6af] max-w-md leading-relaxed font-normal">
        <strong class="font-medium text-white">1 Token</strong> = 1x Audit Leksikal (Tier 1) &bull; <strong class="italic font-medium text-white">2 Token</strong> = 1x Audit Hybrid Lengkap (Tier 1 - 4 + Sertifikat QR).
      </p>
    </div>

    <div class="bg-[#24272c] border border-neutral-700/60 p-5 rounded-[16px] text-xs space-y-2 self-start md:self-auto">
      <div class="font-medium text-white">Metode Pembayaran Resmi</div>
      <div class="text-[#a3a6af] text-[11px] font-normal">Midtrans Payment Gateway (QRIS, VA Bank, E-Wallet)</div>
      <div class="flex items-center justify-between gap-4 pt-1">
        <span class="text-[10px] text-emerald-400 font-medium">
          Status: Real Mode (Live Wallet)
        </span>
        <button
          type="button"
          @click="$emit('topup')"
          class="px-4 py-1.5 bg-white text-[#17191c] rounded-full font-medium text-xs hover:bg-[#f2f2f3] transition-colors"
        >
          Top Up Cepat
        </button>
      </div>
    </div>
  </div>
</template>
