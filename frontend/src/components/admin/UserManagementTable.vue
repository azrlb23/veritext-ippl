<script setup lang="ts">
import { ref, computed } from "vue";
import Badge from "../common/Badge.vue";
import Modal from "../common/Modal.vue";
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
  (
    e: "createUser",
    payload: {
      full_name: string;
      email: string;
      password?: string;
      institution: string;
      role: ManagedUser["role"];
      token_balance: number;
    }
  ): void;
  (e: "updateUser", payload: ManagedUser & { new_password?: string }): void;
  (e: "deleteUser", userId: string): void;
}>();

const searchQuery = ref("");
const roleFilter = ref<string>("ALL");

// Modal states
const isCreateOpen = ref(false);
const isEditOpen = ref(false);
const isDeleteOpen = ref(false);

const showCreatePassword = ref(false);
const showEditPassword = ref(false);

function generateRandomPassword(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$";
  let pwd = "VT#";
  for (let i = 0; i < 7; i++) {
    pwd += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return pwd;
}

const createForm = ref({
  full_name: "",
  email: "",
  password: "VeriText#2026",
  institution: "Institut Teknologi Nasional",
  role: "TRIAL" as ManagedUser["role"],
  token_balance: 10,
});

const editForm = ref<ManagedUser & { new_password?: string }>({
  id: "",
  full_name: "",
  email: "",
  institution: "",
  role: "TRIAL",
  token_balance: 0,
  is_active: true,
  created_at: "",
  new_password: "",
});

const deletingUser = ref<ManagedUser | null>(null);

function openCreate() {
  createForm.value = {
    full_name: "",
    email: "",
    password: generateRandomPassword(),
    institution: "Institut Teknologi Nasional",
    role: "TRIAL",
    token_balance: 10,
  };
  showCreatePassword.value = false;
  isCreateOpen.value = true;
}

function submitCreate() {
  if (!createForm.value.full_name.trim() || !createForm.value.email.trim()) return;
  emit("createUser", {
    full_name: createForm.value.full_name.trim(),
    email: createForm.value.email.trim().toLowerCase(),
    password: createForm.value.password.trim() || "VeriText#2026",
    institution: createForm.value.institution.trim() || "Institut Teknologi Nasional",
    role: createForm.value.role,
    token_balance: Number(createForm.value.token_balance) || 0,
  });
  isCreateOpen.value = false;
}

function openEdit(user: ManagedUser) {
  editForm.value = { ...user, new_password: "" };
  showEditPassword.value = false;
  isEditOpen.value = true;
}

function generateEditPassword() {
  editForm.value.new_password = generateRandomPassword();
  showEditPassword.value = true;
}

function submitEdit() {
  if (!editForm.value.full_name.trim() || !editForm.value.email.trim()) return;
  emit("updateUser", {
    ...editForm.value,
    full_name: editForm.value.full_name.trim(),
    email: editForm.value.email.trim().toLowerCase(),
    institution: editForm.value.institution?.trim() || "Institut Teknologi Nasional",
    token_balance: Number(editForm.value.token_balance) || 0,
    new_password: editForm.value.new_password?.trim() || undefined,
  });
  isEditOpen.value = false;
}

function confirmDelete(user: ManagedUser) {
  deletingUser.value = user;
  isDeleteOpen.value = true;
}

function submitDelete() {
  if (deletingUser.value) {
    emit("deleteUser", deletingUser.value.id);
    isDeleteOpen.value = false;
    deletingUser.value = null;
  }
}

const statusFilter = ref<string>("ALL");
const selectedUserIds = ref<string[]>([]);
const showFilterPopover = ref(false);
const activeDropdownUserId = ref<string | null>(null);

function formatDate(dateStr?: string): string {
  if (!dateStr) return "14 Okt 2025";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

function toggleDropdown(userId: string) {
  if (activeDropdownUserId.value === userId) {
    activeDropdownUserId.value = null;
  } else {
    activeDropdownUserId.value = userId;
  }
}

const filteredUsers = computed(() => {
  return props.users.filter((user) => {
    const matchesRole = roleFilter.value === "ALL" || user.role === roleFilter.value;
    const matchesStatus =
      statusFilter.value === "ALL" ||
      (statusFilter.value === "ACTIVE" && user.is_active) ||
      (statusFilter.value === "INACTIVE" && !user.is_active);
    const q = searchQuery.value.toLowerCase().trim();
    const matchesQuery =
      !q ||
      user.full_name.toLowerCase().includes(q) ||
      user.email.toLowerCase().includes(q) ||
      (user.institution && user.institution.toLowerCase().includes(q));
    return matchesRole && matchesStatus && matchesQuery;
  });
});

const isAllSelected = computed(() => {
  return (
    filteredUsers.value.length > 0 &&
    filteredUsers.value.every((u) => selectedUserIds.value.includes(u.id))
  );
});

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedUserIds.value = [];
  } else {
    selectedUserIds.value = filteredUsers.value.map((u) => u.id);
  }
}

function toggleSelectUser(userId: string) {
  const idx = selectedUserIds.value.indexOf(userId);
  if (idx >= 0) {
    selectedUserIds.value.splice(idx, 1);
  } else {
    selectedUserIds.value.push(userId);
  }
}

function getTokenRatio(balance: number): { pct: number; label: string } {
  const maxBenchmark = Math.max(10, balance);
  const pct = Math.min(100, Math.round((balance / maxBenchmark) * 100));
  return { pct, label: `${balance}/${maxBenchmark}` };
}

defineExpose({
  openCreate,
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
</script>

<template>
  <div class="bg-white border border-[#ededed] rounded-[16px] shadow-sm overflow-hidden space-y-4">
    <!-- Toolbar: Search + Filter Button + Primary Action Button (Zendenta style) -->
    <div class="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <!-- Search Pill -->
      <div class="relative flex-1 max-w-md">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari pengguna, email, atau institusi..."
          class="w-full px-3.5 py-2 pl-9 rounded-full border border-[#e2e8f0] text-xs text-[#1e293b] placeholder:text-[#94a3b8] focus:outline-none focus:border-[#17191c] focus:ring-1 focus:ring-[#17191c] bg-[#f8fafc] font-medium transition-colors"
        />
        <svg class="w-4 h-4 absolute left-3 top-2.5 text-[#94a3b8]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <!-- Right Controls: Filters & + Order Stock style Button -->
      <div class="flex items-center space-x-2.5">
        <!-- Filter Button with Popover -->
        <div class="relative">
          <button
            type="button"
            @click="showFilterPopover = !showFilterPopover"
            class="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg border border-[#e2e8f0] bg-white hover:bg-[#f8fafc] text-xs font-semibold text-[#475569] shadow-sm transition-colors"
          >
            <svg class="w-3.5 h-3.5 text-[#64748b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span>Filters</span>
            <span v-if="roleFilter !== 'ALL' || statusFilter !== 'ALL'" class="w-1.5 h-1.5 rounded-full bg-[#17191c]"></span>
          </button>

          <!-- Filter Popover -->
          <div
            v-if="showFilterPopover"
            class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-[#ededed] p-4 z-30 space-y-3"
          >
            <div>
              <label class="block text-[11px] font-bold text-[#64748b] uppercase tracking-wider mb-1">Peran Akun</label>
              <select
                v-model="roleFilter"
                class="w-full text-xs border border-[#e2e8f0] rounded-lg px-2.5 py-1.5 bg-[#f8fafc] font-medium text-[#1e293b] focus:outline-none focus:border-[#17191c]"
              >
                <option value="ALL">Semua Peran</option>
                <option value="ADMIN">Super Admin</option>
                <option value="REVIEWER">Reviewer (Dosen)</option>
                <option value="PREMIUM">Premium (Peneliti)</option>
                <option value="TRIAL">Trial (Mahasiswa)</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-[#64748b] uppercase tracking-wider mb-1">Status Keaktifan</label>
              <select
                v-model="statusFilter"
                class="w-full text-xs border border-[#e2e8f0] rounded-lg px-2.5 py-1.5 bg-[#f8fafc] font-medium text-[#1e293b] focus:outline-none focus:border-[#17191c]"
              >
                <option value="ALL">Semua Status</option>
                <option value="ACTIVE">Aktif</option>
                <option value="INACTIVE">Nonaktif / Suspend</option>
              </select>
            </div>
            <div class="pt-2 flex justify-between items-center border-t border-[#ededed]">
              <button
                type="button"
                @click="roleFilter = 'ALL'; statusFilter = 'ALL'"
                class="text-[11px] text-[#64748b] hover:text-[#1e293b] font-medium underline"
              >
                Reset
              </button>
              <button
                type="button"
                @click="showFilterPopover = false"
                class="px-2.5 py-1 bg-[#17191c] text-white rounded text-[11px] font-semibold"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>

        <!-- Primary Action Button (+ Tambah Akun) -->
        <button
          type="button"
          @click="openCreate"
          class="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-[#17191c] hover:bg-[#262626] text-white text-xs font-semibold shadow-sm transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span>+ Tambah Akun</span>
        </button>

        <span class="text-xs text-[#64748b] font-medium hidden md:inline">
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
        title="Pengguna Tidak Ditemukan"
        description="Tidak ada data akun pengguna yang cocok dengan kriteria pencarian saat ini."
      />
    </div>

    <!-- User Table (Zendenta Style) -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-[#fafbfc] border-y border-[#ededed] text-[#64748b] font-bold uppercase text-[10px] tracking-wider">
            <th class="py-3 px-4 w-10 text-center">
              <input
                type="checkbox"
                :checked="isAllSelected"
                @change="toggleSelectAll"
                class="rounded border-[#cbd5e1] text-[#17191c] focus:ring-[#17191c] cursor-pointer"
              />
            </th>
            <th class="py-3 px-4">
              <span class="inline-flex items-center space-x-1">
                <span>PENGGUNA / AKUN</span>
                <span class="text-[10px] text-[#94a3b8]">↕</span>
              </span>
            </th>
            <th class="py-3 px-4">
              <span class="inline-flex items-center space-x-1">
                <span>CREATED</span>
                <span class="text-[10px] text-[#94a3b8]">↕</span>
              </span>
            </th>
            <th class="py-3 px-4">
              <span class="inline-flex items-center space-x-1">
                <span>INSTITUSI</span>
                <span class="text-[10px] text-[#94a3b8]">↕</span>
              </span>
            </th>
            <th class="py-3 px-4">
              <span class="inline-flex items-center space-x-1">
                <span>STATUS</span>
                <span class="text-[10px] text-[#94a3b8]">↕</span>
              </span>
            </th>
            <th class="py-3 px-4">
              <span class="inline-flex items-center space-x-1">
                <span>KUOTA TOKEN</span>
                <span class="text-[10px] text-[#94a3b8]">↕</span>
              </span>
            </th>
            <th class="py-3 px-4 text-center">VERIFIKASI</th>
            <th class="py-3 px-4 text-right">AKSI</th>
            <th class="py-3 px-2 w-8"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#ededed]">
          <tr
            v-for="user in filteredUsers"
            :key="user.id"
            class="hover:bg-[#f8fafc] transition-colors group"
            :class="selectedUserIds.includes(user.id) ? 'bg-[#f4f4f5]' : ''"
          >
            <!-- Checkbox -->
            <td class="py-3.5 px-4 text-center">
              <input
                type="checkbox"
                :checked="selectedUserIds.includes(user.id)"
                @change="toggleSelectUser(user.id)"
                class="rounded border-[#cbd5e1] text-[#17191c] focus:ring-[#17191c] cursor-pointer"
              />
            </td>

            <!-- User Info (Order / User equivalent) -->
            <td class="py-3.5 px-4">
              <div class="flex items-center space-x-2.5">
                <div class="w-7 h-7 rounded-full bg-[#f1f5f9] border border-[#e2e8f0] text-[#334155] font-bold text-xs flex items-center justify-center shrink-0">
                  {{ user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U' }}
                </div>
                <div>
                  <div class="font-bold text-[#1e293b] leading-snug">{{ user.full_name }}</div>
                  <div class="text-[11px] text-[#64748b] flex items-center space-x-1.5">
                    <span>#VT{{ user.id.substring(0, 6) }}</span>
                    <span>•</span>
                    <span class="truncate max-w-[140px]">{{ user.email }}</span>
                    <span>•</span>
                    <Badge :variant="getRoleVariant(user.role)" size="xs">
                      {{ user.role }}
                    </Badge>
                  </div>
                </div>
              </div>
            </td>

            <!-- Created Date -->
            <td class="py-3.5 px-4 text-[#475569] font-medium whitespace-nowrap">
              {{ formatDate(user.created_at) }}
            </td>

            <!-- Institution (From Vendor equivalent) -->
            <td class="py-3.5 px-4 text-[#334155] font-medium">
              <div class="flex items-center space-x-1.5 max-w-[180px]">
                <svg class="w-3.5 h-3.5 text-[#64748b] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span class="truncate">{{ user.institution || 'Institut Teknologi Nasional' }}</span>
              </div>
            </td>

            <!-- Status Pill (Zendenta style) -->
            <td class="py-3.5 px-4">
              <span
                v-if="user.is_active"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-[#ecfdf5] text-[#065f46] border border-[#a7f3d0]"
              >
                AKTIF
              </span>
              <span
                v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-[#fef2f2] text-[#991b1b] border border-[#fecaca]"
              >
                SUSPEND
              </span>
            </td>

            <!-- Token Ratio (Item Received equivalent) -->
            <td class="py-3.5 px-4">
              <div class="space-y-1">
                <div class="flex items-center justify-between text-[11px] font-bold text-[#1e293b] tabular-nums">
                  <span>{{ getTokenRatio(user.token_balance).label }}</span>
                  <button
                    type="button"
                    @click="emit('adjustTokens', user.id, 5)"
                    class="text-[10px] text-[#17191c] hover:underline font-semibold ml-2"
                    title="Tambah 5 token"
                  >
                    +5 Token
                  </button>
                </div>
                <div class="w-24 bg-[#e2e8f0] h-1.5 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-300"
                    :class="user.token_balance >= 3 ? 'bg-[#17191c]' : 'bg-[#ef4444]'"
                    :style="{ width: `${getTokenRatio(user.token_balance).pct}%` }"
                  ></div>
                </div>
              </div>
            </td>

            <!-- Verification (Send Email check equivalent) -->
            <td class="py-3.5 px-4 text-center">
              <div class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-[#ecfdf5] text-[#10b981]">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </td>

            <!-- Action Button (Receive equivalent -> Kelola) -->
            <td class="py-3.5 px-4 text-right whitespace-nowrap">
              <button
                type="button"
                @click="openEdit(user)"
                class="px-3 py-1 text-xs font-semibold rounded-md border border-[#cbd5e1] text-[#334155] bg-white hover:bg-[#f1f5f9] transition-colors shadow-sm"
              >
                Kelola
              </button>
            </td>

            <!-- Kebab Menu -->
            <td class="py-3.5 px-2 relative text-right">
              <button
                type="button"
                @click.stop="toggleDropdown(user.id)"
                class="p-1 rounded text-[#94a3b8] hover:text-[#1e293b] hover:bg-[#e2e8f0] transition-colors"
                title="Aksi lainnya"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="5" r="2" />
                  <circle cx="12" cy="12" r="2" />
                  <circle cx="12" cy="19" r="2" />
                </svg>
              </button>

              <!-- Dropdown Menu -->
              <div
                v-if="activeDropdownUserId === user.id"
                class="absolute right-2 mt-1 w-44 bg-white rounded-lg shadow-lg border border-[#ededed] py-1 z-40 text-left text-xs"
              >
                <button
                  type="button"
                  @click="emit('adjustTokens', user.id, 5); activeDropdownUserId = null"
                  class="w-full text-left px-3 py-1.5 hover:bg-[#f8fafc] text-[#1e293b] flex items-center space-x-2"
                >
                  <svg class="w-3.5 h-3.5 text-[#17191c]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Tambah 5 Token</span>
                </button>
                <button
                  type="button"
                  @click="openEdit(user); activeDropdownUserId = null"
                  class="w-full text-left px-3 py-1.5 hover:bg-[#f8fafc] text-[#1e293b] flex items-center space-x-2"
                >
                  <svg class="w-3.5 h-3.5 text-[#64748b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  <span>Edit Profil & Sandi</span>
                </button>
                <button
                  type="button"
                  @click="emit('toggleStatus', user.id); activeDropdownUserId = null"
                  class="w-full text-left px-3 py-1.5 hover:bg-[#f8fafc] flex items-center space-x-2"
                  :class="user.is_active ? 'text-[#b91c1c]' : 'text-[#065f46]'"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                  <span>{{ user.is_active ? 'Suspend Akun' : 'Aktifkan Akun' }}</span>
                </button>
                <div class="border-t border-[#ededed] my-1"></div>
                <button
                  type="button"
                  @click="confirmDelete(user); activeDropdownUserId = null"
                  class="w-full text-left px-3 py-1.5 hover:bg-red-50 text-red-600 flex items-center space-x-2"
                >
                  <svg class="w-3.5 h-3.5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Hapus Akun</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal 1: Tambah Pengguna Baru (Create) -->
    <Modal
      :isOpen="isCreateOpen"
      title="Tambah Akun Pengguna Baru"
      maxWidth="md"
      @close="isCreateOpen = false"
    >
      <form @submit.prevent="submitCreate" class="space-y-3.5">
        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Nama Lengkap <span class="text-red-500">*</span>
          </label>
          <input
            v-model="createForm.full_name"
            type="text"
            required
            placeholder="misal: Dr. Irfan Hakim, M.Kom"
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Alamat Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="createForm.email"
            type="email"
            required
            placeholder="misal: irfan.hakim@kampus.ac.id"
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Institusi / Universitas
          </label>
          <input
            v-model="createForm.institution"
            type="text"
            placeholder="Institut Teknologi Nasional"
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-xs font-bold text-audyr-ink">
              Kata Sandi Akun <span class="text-red-500">*</span>
            </label>
            <button
              type="button"
              @click="createForm.password = generateRandomPassword()"
              class="text-[11px] text-audyr-slate hover:text-audyr-ink font-semibold underline underline-offset-2 transition-colors"
            >
              Acak Sandi
            </button>
          </div>
          <div class="relative">
            <input
              v-model="createForm.password"
              :type="showCreatePassword ? 'text' : 'password'"
              required
              minlength="6"
              placeholder="Minimal 6 karakter"
              class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink font-mono pr-20"
            />
            <button
              type="button"
              @click="showCreatePassword = !showCreatePassword"
              class="absolute right-2 top-2 text-[10px] uppercase font-bold text-audyr-ash hover:text-audyr-ink px-1.5 py-0.5 rounded border border-[#ededed] bg-white transition-colors"
            >
              {{ showCreatePassword ? 'Sembunyi' : 'Lihat' }}
            </button>
          </div>
          <p class="text-[10px] text-audyr-ash mt-1 font-normal">
            Kata sandi awal yang diberikan kepada pengguna untuk login pertama kali.
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-audyr-ink mb-1">
              Peran Akun
            </label>
            <select
              v-model="createForm.role"
              class="w-full px-2.5 py-2 text-xs rounded-[4px] border border-[#ededed] bg-white text-audyr-ink focus:outline-none focus:border-audyr-ink font-semibold"
            >
              <option value="TRIAL">TRIAL (Mahasiswa)</option>
              <option value="PREMIUM">PREMIUM (Peneliti)</option>
              <option value="REVIEWER">REVIEWER (Dosen)</option>
              <option value="ADMIN">ADMIN (Super Admin)</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-audyr-ink mb-1">
              Saldo Token Awal
            </label>
            <input
              v-model.number="createForm.token_balance"
              type="number"
              min="0"
              class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink font-bold tabular-nums"
            />
          </div>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="isCreateOpen = false"
          class="px-3 py-1.5 text-xs font-semibold rounded-[4px] border border-[#ededed] text-audyr-ash hover:text-audyr-ink transition-colors"
        >
          Batal
        </button>
        <button
          type="button"
          @click="submitCreate"
          class="px-4 py-1.5 text-xs font-bold rounded-[4px] bg-audyr-ink text-white hover:bg-audyr-charcoal transition-colors"
        >
          Simpan Pengguna
        </button>
      </template>
    </Modal>

    <!-- Modal 2: Edit Data Pengguna (Update) -->
    <Modal
      :isOpen="isEditOpen"
      title="Edit Profil & Kuota Pengguna"
      maxWidth="md"
      @close="isEditOpen = false"
    >
      <form @submit.prevent="submitEdit" class="space-y-3.5">
        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Nama Lengkap <span class="text-red-500">*</span>
          </label>
          <input
            v-model="editForm.full_name"
            type="text"
            required
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Alamat Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="editForm.email"
            type="email"
            required
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-audyr-ink mb-1">
            Institusi / Universitas
          </label>
          <input
            v-model="editForm.institution"
            type="text"
            class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-audyr-ink mb-1">
              Peran Akun
            </label>
            <select
              v-model="editForm.role"
              class="w-full px-2.5 py-2 text-xs rounded-[4px] border border-[#ededed] bg-white text-audyr-ink focus:outline-none focus:border-audyr-ink font-semibold"
            >
              <option value="TRIAL">TRIAL</option>
              <option value="PREMIUM">PREMIUM</option>
              <option value="REVIEWER">REVIEWER</option>
              <option value="ADMIN">ADMIN</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-audyr-ink mb-1">
              Saldo Kuota Token
            </label>
            <input
              v-model.number="editForm.token_balance"
              type="number"
              min="0"
              class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink font-bold tabular-nums"
            />
          </div>
        </div>

        <!-- Reset / Ubah Password -->
        <div class="p-3 bg-[#fafafa] rounded-[4px] border border-[#ededed] space-y-2">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-bold text-audyr-ink">
              Reset / Ubah Kata Sandi Baru
            </label>
            <button
              type="button"
              @click="generateEditPassword"
              class="text-[11px] text-audyr-slate hover:text-audyr-ink font-semibold underline underline-offset-2 transition-colors"
            >
              Acak Sandi Baru
            </button>
          </div>
          <div class="relative">
            <input
              v-model="editForm.new_password"
              :type="showEditPassword ? 'text' : 'password'"
              minlength="6"
              placeholder="Kosongkan jika tidak ingin mengubah sandi..."
              class="w-full px-3 py-2 text-xs rounded-[4px] border border-[#ededed] text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink font-mono pr-20 bg-white"
            />
            <button
              type="button"
              @click="showEditPassword = !showEditPassword"
              class="absolute right-2 top-2 text-[10px] uppercase font-bold text-audyr-ash hover:text-audyr-ink px-1.5 py-0.5 rounded border border-[#ededed] bg-white transition-colors"
            >
              {{ showEditPassword ? 'Sembunyi' : 'Lihat' }}
            </button>
          </div>
          <p class="text-[10px] text-audyr-ash leading-relaxed font-normal">
            Jika diisi (minimal 6 karakter), kata sandi akun pengguna ini akan langsung ditimpa/direset oleh admin.
          </p>
        </div>

        <div class="pt-2 flex items-center justify-between border-t border-[#ededed]">
          <span class="text-xs font-bold text-audyr-ink">Status Akun Aktif</span>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              v-model="editForm.is_active"
              type="checkbox"
              class="sr-only peer"
            />
            <div class="w-9 h-5 bg-[#ededed] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#ededed] after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#262626]"></div>
          </label>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="isEditOpen = false"
          class="px-3 py-1.5 text-xs font-semibold rounded-[4px] border border-[#ededed] text-audyr-ash hover:text-audyr-ink transition-colors"
        >
          Batal
        </button>
        <button
          type="button"
          @click="submitEdit"
          class="px-4 py-1.5 text-xs font-bold rounded-[4px] bg-audyr-ink text-white hover:bg-audyr-charcoal transition-colors"
        >
          Simpan Perubahan
        </button>
      </template>
    </Modal>

    <!-- Modal 3: Konfirmasi Hapus Akun (Delete) -->
    <Modal
      :isOpen="isDeleteOpen"
      title="Konfirmasi Penghapusan Akun"
      maxWidth="sm"
      @close="isDeleteOpen = false"
    >
      <div class="space-y-3" v-if="deletingUser">
        <p class="text-xs text-audyr-slate leading-relaxed">
          Apakah Anda yakin ingin menghapus akun pengguna berikut secara permanen?
        </p>
        <div class="p-3 bg-[#fafafa] rounded-[4px] border border-[#ededed] text-xs">
          <div class="font-bold text-audyr-ink">{{ deletingUser.full_name }}</div>
          <div class="text-[11px] text-audyr-ash">{{ deletingUser.email }}</div>
          <div class="text-[11px] text-audyr-slate mt-1">Peran: {{ deletingUser.role }} &bull; Saldo: {{ deletingUser.token_balance }} Token</div>
        </div>
        <p class="text-[11px] text-red-600 font-semibold leading-relaxed">
          Peringatan: Seluruh data riwayat audit, dompet token, dan catatan terkait pengguna ini akan dihapus dari basis data sesuai ketentuan UU PDP No. 27/2022.
        </p>
      </div>

      <template #footer>
        <button
          type="button"
          @click="isDeleteOpen = false"
          class="px-3 py-1.5 text-xs font-semibold rounded-[4px] border border-[#ededed] text-audyr-ash hover:text-audyr-ink transition-colors"
        >
          Batal
        </button>
        <button
          type="button"
          @click="submitDelete"
          class="px-4 py-1.5 text-xs font-bold rounded-[4px] bg-red-600 text-white hover:bg-red-700 transition-colors shadow-audyr-subtle"
        >
          Ya, Hapus Pengguna
        </button>
      </template>
    </Modal>
  </div>
</template>
