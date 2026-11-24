<script setup lang="ts">
import type { AdminUserItem } from "../../types/admin";

defineProps<{
  users: AdminUserItem[];
  loading?: boolean;
  page: number;
  pages: number;
  total: number;
  search?: string;
  selectedRole?: string;
}>();

const emit = defineEmits<{
  (e: "update:search", v: string): void;
  (e: "update:selectedRole", v: string): void;
  (e: "changePage", v: number): void;
}>();

const ROLES = [
  { key: "", label: "Semua" },
  { key: "FREE", label: "FREE" },
  { key: "PREMIUM", label: "PREMIUM" },
  { key: "ADMIN", label: "ADMIN" },
];

const rolePill = (role: string) => {
  const r = (role || "").toUpperCase();
  if (r === "PREMIUM") return "bg-[#FEF3C7] text-[#B45309]";
  if (r === "ADMIN") return "bg-[#F1F5F4] text-[#4B4757]";
  return "bg-[#EBF8F6] text-[#0F766E]";
};

const statusLabel = (u: AdminUserItem) => (u.is_locked ? "Terkunci" : u.is_active ? "Aktif" : "Nonaktif");
const statusTone = (u: AdminUserItem) => (u.is_locked ? "text-[#B91C1C]" : u.is_active ? "text-[#047857]" : "text-[#5E5A6B]");
const formatDate = (d?: string | null) => (d ? new Date(d).toLocaleDateString("id-ID", { dateStyle: "medium" }) : "-");
const navCls = "vt-btn-light inline-flex h-10 cursor-pointer items-center rounded-full px-5 text-[14px] font-semibold transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:cursor-not-allowed disabled:opacity-40";
</script>

<template>
  <section class="rounded-[28px] border border-[#E8ECEB] bg-white p-6 sm:p-8" aria-labelledby="users-table-title" :aria-busy="loading">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 id="users-table-title" class="text-[20px] font-semibold tracking-[-0.03em] text-[#14111C]">Daftar pengguna</h2>
        <p class="mt-1 text-[14px] tabular-nums text-[#5E5A6B]">{{ total.toLocaleString("id-ID") }} pengguna terdaftar</p>
      </div>
      <input
        type="search"
        :value="search || ''"
        placeholder="Cari nama atau email..."
        aria-label="Cari nama atau email pengguna"
        class="w-full border-0 border-b-[3px] border-[#E8ECEB] bg-transparent py-2 text-[15px] text-[#14111C] placeholder-[#5E5A6B] transition-colors duration-150 focus:border-[#0F766E] focus:outline-none sm:max-w-xs"
        @input="emit('update:search', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <div class="mt-5 flex flex-wrap gap-2" role="group" aria-label="Saring peran pengguna">
      <button
        v-for="r in ROLES"
        :key="r.key"
        type="button"
        :aria-pressed="(selectedRole || '') === r.key"
        class="inline-flex h-10 cursor-pointer items-center rounded-full px-4 text-[13px] font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        :class="(selectedRole || '') === r.key ? 'vt-btn-dark' : 'vt-btn-light'"
        @click="emit('update:selectedRole', r.key)"
      >
        {{ r.label }}
      </button>
    </div>

    <p v-if="!loading && users.length === 0" class="py-12 text-center text-[15px] text-[#5E5A6B]">Tidak ada pengguna yang sesuai.</p>

    <ul v-if="users.length > 0" class="mt-5 divide-y divide-[#E8ECEB] md:hidden">
      <li v-for="u in users" :key="u.id" class="py-4">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate text-[15px] font-semibold text-[#14111C]">{{ u.full_name }}</p>
            <p class="truncate text-[13px] text-[#5E5A6B]">{{ u.email }}</p>
          </div>
          <span class="flex-shrink-0 rounded-full px-2.5 py-0.5 text-[12px] font-semibold" :class="rolePill(u.role)">{{ u.role }}</span>
        </div>
        <div class="mt-2.5 flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-[13px] tabular-nums text-[#4B4757]">
          <span>Token: <strong class="text-[#14111C]">{{ u.balance }}</strong> · Trial: <strong class="text-[#14111C]">{{ u.ai_trial_remaining }}</strong> · Audit: <strong class="text-[#14111C]">{{ u.audit_count }}</strong></span>
          <span class="font-medium" :class="statusTone(u)">{{ statusLabel(u) }}</span>
        </div>
        <p class="mt-1 text-[12px] text-[#5E5A6B]">Terdaftar {{ formatDate(u.created_at) }}</p>
      </li>
    </ul>

    <div v-if="users.length > 0" class="mt-5 hidden overflow-x-auto md:block">
      <table class="w-full border-collapse text-left text-[14px]">
        <thead>
          <tr class="border-b border-[#E8ECEB] text-[12px] font-semibold uppercase tracking-[0.04em] text-[#5E5A6B]">
            <th class="py-3 pr-4">Pengguna</th>
            <th class="px-3 py-3">Peran</th>
            <th class="px-3 py-3 text-right">Saldo token</th>
            <th class="px-3 py-3 text-right">Trial AI</th>
            <th class="px-3 py-3 text-right">Audit</th>
            <th class="px-3 py-3">Tanggal daftar</th>
            <th class="py-3 pl-3 text-right">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#E8ECEB]">
          <tr v-for="u in users" :key="u.id" class="transition-colors duration-150 hover:bg-[#F8FBFA]">
            <td class="py-3.5 pr-4">
              <p class="font-semibold text-[#14111C]">{{ u.full_name }}</p>
              <p class="text-[13px] text-[#5E5A6B]">{{ u.email }}</p>
            </td>
            <td class="px-3 py-3.5">
              <span class="inline-block rounded-full px-2.5 py-0.5 text-[12px] font-semibold" :class="rolePill(u.role)">{{ u.role }}</span>
            </td>
            <td class="px-3 py-3.5 text-right font-semibold tabular-nums text-[#14111C]">{{ u.balance.toLocaleString("id-ID") }}</td>
            <td class="px-3 py-3.5 text-right tabular-nums text-[#4B4757]">{{ u.ai_trial_remaining.toLocaleString("id-ID") }}</td>
            <td class="px-3 py-3.5 text-right tabular-nums text-[#4B4757]">{{ u.audit_count.toLocaleString("id-ID") }}</td>
            <td class="px-3 py-3.5 text-[#5E5A6B]">{{ formatDate(u.created_at) }}</td>
            <td class="py-3.5 pl-3 text-right font-semibold" :class="statusTone(u)">{{ statusLabel(u) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="pages > 1" class="mt-6 flex items-center justify-between gap-3">
      <button type="button" :class="navCls" :disabled="page <= 1" @click="emit('changePage', page - 1)">Sebelumnya</button>
      <span class="text-[14px] tabular-nums text-[#5E5A6B]">{{ page }} / {{ pages }}</span>
      <button type="button" :class="navCls" :disabled="page >= pages" @click="emit('changePage', page + 1)">Berikutnya</button>
    </div>
  </section>
</template>
