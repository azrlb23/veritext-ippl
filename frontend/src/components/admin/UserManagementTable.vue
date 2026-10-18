<script setup lang="ts">
import { ref, computed } from "vue";
import Badge from "../common/Badge.vue";
import EmptyState from "../common/EmptyState.vue";
import SkeletonLoader from "../common/SkeletonLoader.vue";
import type { ManagedUser } from "../../types/admin";

interface Props {
  users: ManagedUser[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: "toggleStatus", userId: string): void;
  (e: "adjustTokens", userId: string, delta: number): void;
  (e: "changeRole", userId: string, role: ManagedUser["role"]): void;
}>();

const searchQuery = ref("");
const roleFilter = ref<string>("ALL");

const filteredUsers = computed(() => {
  return props.users.filter((user) => {
    const matchesRole = roleFilter.value === "ALL" || user.role === roleFilter.value;
    const q = searchQuery.value.toLowerCase().trim();
    const matchesQuery =
      !q ||
      user.full_name.toLowerCase().includes(q) ||
      user.email.toLowerCase().includes(q) ||
      (user.institution && user.institution.toLowerCase().includes(q));
    return matchesRole && matchesQuery;
  });
});

function getRoleVariant(role: string): "danger" | "secondary" | "primary" | "neutral" {
  switch (role) {
    case "ADMIN":
      return "danger";
    case "REVIEWER":
      return "secondary";
    case "PREMIUM":
      return "primary";
    case "TRIAL":
    default:
      return "neutral";
  }
}

function onRoleSelect(userId: string, event: Event) {
  const target = event.target as HTMLSelectElement;
  emit("changeRole", userId, target.value as ManagedUser["role"]);
}
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[14px] shadow-audyr-subtle overflow-hidden space-y-4">
    <!-- Header & Search Controls -->
    <div class="p-5 border-b border-[#ededed] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-tight text-audyr-ink">
          Manajemen Pengguna & Kuota Token
        </h3>
        <p class="text-xs text-audyr-ash mt-0.5">Daftar akun dan hak akses pengguna sistem VeriText AI</p>
      </div>

      <div class="flex flex-wrap items-center gap-2.5">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cari nama / email..."
            class="px-3 py-1.5 pl-7 rounded-[4px] border border-[#ededed] text-xs text-audyr-ink placeholder:text-audyr-fog focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white w-44 sm:w-56"
          />
          <span class="absolute left-2 top-2 text-audyr-ash text-xs">🔍</span>
        </div>

        <select
          v-model="roleFilter"
          class="px-2.5 py-1.5 rounded-[4px] border border-[#ededed] text-xs bg-white text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
        >
          <option value="ALL">Semua Peran</option>
          <option value="ADMIN">Admin</option>
          <option value="REVIEWER">Reviewer</option>
          <option value="PREMIUM">Premium</option>
          <option value="TRIAL">Trial</option>
        </select>

        <span class="text-xs text-audyr-ash font-mono hidden md:inline">
          ({{ filteredUsers.length }}/{{ users.length }})
        </span>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="p-6">
      <SkeletonLoader shape="table-row" :count="4" />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredUsers.length === 0" class="p-8">
      <EmptyState
        icon="👥"
        title="Pengguna Tidak Ditemukan"
        description="Tidak ada data akun pengguna yang cocok dengan kriteria pencarian saat ini."
      />
    </div>

    <!-- User Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-white border-y border-[#ededed] text-audyr-ash font-medium uppercase text-[11px] tracking-tight">
            <th class="py-3 px-5">Nama & Email</th>
            <th class="py-3 px-4">Institusi</th>
            <th class="py-3 px-4">Peran (Role)</th>
            <th class="py-3 px-4">Saldo Token</th>
            <th class="py-3 px-4">Status</th>
            <th class="py-3 px-5 text-right">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-[#fafafa] transition-colors">
            <td class="py-3.5 px-5">
              <div class="font-semibold text-audyr-ink">{{ user.full_name }}</div>
              <div class="text-[11px] text-audyr-ash font-mono">{{ user.email }}</div>
            </td>
            <td class="py-3.5 px-4 text-audyr-slate">{{ user.institution || '-' }}</td>
            <td class="py-3.5 px-4">
              <div class="flex items-center space-x-1.5">
                <Badge :variant="getRoleVariant(user.role)" size="xs">
                  {{ user.role }}
                </Badge>
                <select
                  :value="user.role"
                  @change="onRoleSelect(user.id, $event)"
                  class="text-[10px] bg-white border border-[#ededed] rounded-[4px] px-1.5 py-0.5 text-audyr-ink focus:outline-none focus:border-audyr-ink cursor-pointer"
                  title="Ubah peran pengguna"
                >
                  <option value="TRIAL">TRIAL</option>
                  <option value="PREMIUM">PREMIUM</option>
                  <option value="REVIEWER">REVIEWER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>
            </td>
            <td class="py-3.5 px-4 font-mono font-bold text-audyr-ink">
              <div class="flex items-center space-x-2">
                <span>{{ user.token_balance }}</span>
                <button
                  type="button"
                  @click="emit('adjustTokens', user.id, 5)"
                  class="text-[10px] bg-transparent border border-[#ededed] hover:bg-[#ededed] text-audyr-ink px-1.5 py-0.5 rounded-[4px] font-mono transition-colors"
                  title="Tambah 5 token"
                >
                  +5
                </button>
              </div>
            </td>
            <td class="py-3.5 px-4">
              <Badge :variant="user.is_active ? 'success' : 'danger'" size="xs" dot>
                {{ user.is_active ? 'Aktif' : 'Nonaktif' }}
              </Badge>
            </td>
            <td class="py-3.5 px-5 text-right whitespace-nowrap space-x-2">
              <button
                type="button"
                @click="emit('toggleStatus', user.id)"
                class="text-xs font-medium px-2.5 py-1 rounded-[4px] border transition-colors tracking-tight"
                :class="user.is_active ? 'text-red-600 border-red-200 hover:bg-red-50' : 'text-[#065f46] border-[#a7f3d0] hover:bg-audyr-mint-whisper'"
              >
                {{ user.is_active ? 'Suspend' : 'Aktifkan' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
