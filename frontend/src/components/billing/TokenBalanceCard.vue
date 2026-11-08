<script setup lang="ts">
interface Props {
  balance: number;
  role?: string;
}

withDefaults(defineProps<Props>(), {
  role: "FREE",
});

defineEmits<{
  (e: "topup"): void;
}>();
</script>

<template>
  <div class="bg-[#F8FAFC] rounded-[28px] border border-[#E4E8F0] p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 font-sans">
    <div class="space-y-3">
      <div class="flex items-center space-x-2.5">
        <span class="text-xs uppercase tracking-wider text-[#5B6475] font-bold">Dompet Saldo Token Audit</span>
        <span
          v-if="role === 'PREMIUM'"
          class="px-3 py-0.5 rounded-full text-[10px] font-bold tracking-wider bg-[#EAF7EE] text-[#15803D] border border-[#A7F3D0] uppercase"
        >
          PREMIUM
        </span>
        <span
          v-else
          class="px-3 py-0.5 rounded-full text-[10px] font-bold tracking-wider bg-[#F1F5F9] text-[#5B6475] border border-[#E4E8F0] uppercase"
        >
          TRIAL
        </span>
      </div>
      <div class="flex items-baseline space-x-3">
        <span class="text-4xl sm:text-5xl font-extrabold tracking-tight text-[#0B0F19] tabular-nums">{{ balance }}</span>
        <span class="text-sm text-[#5B6475] font-medium">Token Tersedia</span>
      </div>
      <p class="text-xs text-[#5B6475] max-w-md leading-relaxed font-normal">
        <strong class="font-semibold text-[#0B0F19]">1 Token</strong> = 1x Audit Leksikal (Tier 1) - <strong class="font-semibold text-[#0B0F19]">2 Token</strong> = 1x Audit Hybrid Lengkap (Tier 1 - 4 + Sertifikat QR).
      </p>
    </div>

    <div class="bg-white border border-[#E4E8F0] p-5 rounded-[20px] text-xs space-y-2.5 self-start md:self-auto shadow-xs">
      <div class="font-semibold text-[#0B0F19]">Metode Pembayaran Resmi</div>
      <div class="text-[#5B6475] text-[11.5px] font-normal">Midtrans Payment Gateway (QRIS, VA Bank, E-Wallet)</div>
      <div class="flex items-center justify-between gap-4 pt-1">
        <span class="text-[11px] text-[#15803D] font-medium flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-[#15803D] inline-block animate-pulse"></span>
          <span>Status: Real Mode (Live Wallet)</span>
        </span>
        <button
          type="button"
          @click="$emit('topup')"
          class="px-4 py-2 bg-[#1560BD] hover:bg-[#1A73D9] text-white rounded-full font-semibold text-xs shadow-xs transition-all active:scale-[0.98] cursor-pointer"
        >
          Top Up Cepat &rarr;
        </button>
      </div>
    </div>
  </div>
</template>
