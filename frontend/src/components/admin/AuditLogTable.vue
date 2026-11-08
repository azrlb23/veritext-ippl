<script setup lang="ts">
interface AuditLogItem {
  id: string;
  action_type: string;
  actor_ip?: string | null;
  action_result: string;
  created_at: string;
}

defineProps<{ logs: AuditLogItem[]; loading?: boolean; page: number; pages: number; total: number; selectedAction?: string }>();
const emit = defineEmits<{ (e: "update:selectedAction", v: string): void; (e: "changePage", v: number): void }>();

const FILTERS = [
  { key: "", label: "Semua" },
  { key: "AUTH_LOGIN", label: "Masuk" },
  { key: "AUDIT_SUBMIT", label: "Pemeriksaan" },
  { key: "TOKEN_DEBIT", label: "Token" },
  { key: "BILLING_TOPUP", label: "Pembelian" },
  { key: "DOCUMENT_PURGE", label: "Hapus naskah" },
];
const actionLabel = (a: string) => FILTERS.find((f) => f.key === a)?.label || a;
const date = (d?: string | null) => (d ? new Date(d).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" }) : "-");
const failed = (r: string) => r.toUpperCase() !== "SUCCESS";
const nav = "inline-flex h-11 cursor-pointer items-center rounded-full bg-[#F3EEFA] px-5 text-[14px] font-semibold text-[#14111C] transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] disabled:cursor-not-allowed disabled:opacity-40";
</script>

<template>
  <section class="h-full rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="log-judul" :aria-busy="loading">
    <h2 id="log-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Catatan aktivitas</h2>
    <p class="mt-1 text-[14px] text-[#5E5A6B]">{{ total.toLocaleString("id-ID") }} catatan</p>
    <div class="mt-4 flex flex-wrap gap-2" role="group" aria-label="Saring aktivitas">
      <button v-for="f in FILTERS" :key="f.key" type="button" :aria-pressed="(selectedAction || '') === f.key" class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]" :class="(selectedAction || '') === f.key ? 'bg-[#14111C] text-white shadow-btn-dark' : 'bg-[#F3EEFA] text-[#14111C]'" @click="emit('update:selectedAction', f.key)">{{ f.label }}</button>
    </div>
    <p v-if="!loading && logs.length === 0" class="py-12 text-center text-[15px] text-[#5E5A6B]">Belum ada catatan.</p>
    <ul v-else class="mt-3 divide-y divide-[#14111C]/[0.06]">
      <li v-for="l in logs" :key="l.id" class="flex items-center justify-between gap-4 py-4">
        <div class="min-w-0">
          <p class="truncate text-[15px] font-semibold text-[#14111C]">{{ actionLabel(l.action_type) }}</p>
          <p class="text-[13px] text-[#5E5A6B]">{{ date(l.created_at) }}<span v-if="l.actor_ip"> &middot; {{ l.actor_ip }}</span></p>
        </div>
        <p class="flex-shrink-0 text-[14px] font-medium" :class="failed(l.action_result) ? 'text-[#B91C1C]' : 'text-[#5E5A6B]'">{{ failed(l.action_result) ? "Gagal" : "Berhasil" }}</p>
      </li>
    </ul>
    <div v-if="pages > 1" class="mt-5 flex items-center justify-between gap-3">
      <button type="button" :class="nav" :disabled="page <= 1" @click="emit('changePage', page - 1)">Sebelumnya</button>
      <span class="text-[14px] tabular-nums text-[#5E5A6B]">{{ page }} / {{ pages }}</span>
      <button type="button" :class="nav" :disabled="page >= pages" @click="emit('changePage', page + 1)">Berikutnya</button>
    </div>
  </section>
</template>
