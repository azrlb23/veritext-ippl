<script setup lang="ts">
import { ref, computed } from "vue";
import Badge from "../common/Badge.vue";
import Button from "../common/Button.vue";
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
      institution: string;
      role: ManagedUser["role"];
      token_balance: number;
    }
  ): void;
  (e: "updateUser", payload: ManagedUser): void;
  (e: "deleteUser", userId: string): void;
}>();

const searchQuery = ref("");
const roleFilter = ref<string>("ALL");

// Modal states
const isCreateOpen = ref(false);
const isEditOpen = ref(false);
const isDeleteOpen = ref(false);

const createForm = ref({
  full_name: "",
  email: "",
  institution: "Institut Teknologi Nasional",
  role: "TRIAL" as ManagedUser["role"],
  token_balance: 10,
});

const editForm = ref<ManagedUser>({
  id: "",
  full_name: "",
  email: "",
  institution: "",
  role: "TRIAL",
  token_balance: 0,
  is_active: true,
  created_at: "",
});

const deletingUser = ref<ManagedUser | null>(null);

function openCreate() {
  createForm.value = {
    full_name: "",
    email: "",
    institution: "Institut Teknologi Nasional",
    role: "TRIAL",
    token_balance: 10,
  };
  isCreateOpen.value = true;
}

function submitCreate() {
  if (!createForm.value.full_name.trim() || !createForm.value.email.trim()) return;
  emit("createUser", {
    full_name: createForm.value.full_name.trim(),
    email: createForm.value.email.trim().toLowerCase(),
    institution: createForm.value.institution.trim() || "Institut Teknologi Nasional",
    role: createForm.value.role,
    token_balance: Number(createForm.value.token_balance) || 0,
  });
  isCreateOpen.value = false;
}

function openEdit(user: ManagedUser) {
  editForm.value = { ...user };
  isEditOpen.value = true;
}

function submitEdit() {
  if (!editForm.value.full_name.trim() || !editForm.value.email.trim()) return;
  emit("updateUser", {
    ...editForm.value,
    full_name: editForm.value.full_name.trim(),
    email: editForm.value.email.trim().toLowerCase(),
    institution: editForm.value.institution?.trim() || "Institut Teknologi Nasional",
    token_balance: Number(editForm.value.token_balance) || 0,
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
        <h3 class="text-sm font-extrabold uppercase tracking-wider text-audyr-ink">
          Manajemen Pengguna & Kuota Token
        </h3>
        <p class="text-xs text-audyr-ash mt-0.5 font-normal">Daftar akun dan hak akses pengguna sistem VeriText AI</p>
      </div>

      <div class="flex flex-wrap items-center gap-2.5">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cari nama / email..."
            class="px-3 py-1.5 pl-8 rounded-[4px] border border-[#ededed] text-xs text-audyr-ink placeholder:text-audyr-fog focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink bg-white w-44 sm:w-56 font-medium"
          />
          <svg class="w-3.5 h-3.5 absolute left-2.5 top-2 text-[#929292]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <select
          v-model="roleFilter"
          class="px-2.5 py-1.5 rounded-[4px] border border-[#ededed] text-xs bg-white text-audyr-ink focus:outline-none focus:border-audyr-ink focus:ring-1 focus:ring-audyr-ink font-semibold"
        >
          <option value="ALL">Semua Peran</option>
          <option value="ADMIN">Admin</option>
          <option value="REVIEWER">Reviewer</option>
          <option value="PREMIUM">Premium</option>
          <option value="TRIAL">Trial</option>
        </select>

        <Button
          variant="primary"
          size="sm"
          @click="openCreate"
          class="text-xs"
        >
          + Tambah Pengguna
        </Button>

        <span class="text-xs text-audyr-ash font-bold hidden md:inline">
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

    <!-- User Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse text-xs">
        <thead>
          <tr class="bg-white border-y border-[#ededed] text-audyr-ash font-bold uppercase text-[11px] tracking-wider">
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
              <div class="font-bold text-audyr-ink">{{ user.full_name }}</div>
              <div class="text-[11px] text-audyr-ash font-medium">{{ user.email }}</div>
            </td>
            <td class="py-3.5 px-4 text-audyr-slate font-medium">{{ user.institution || '-' }}</td>
            <td class="py-3.5 px-4">
              <div class="flex items-center space-x-1.5">
                <Badge :variant="getRoleVariant(user.role)" size="xs">
                  {{ user.role }}
                </Badge>
                <select
                  :value="user.role"
                  @change="onRoleSelect(user.id, $event)"
                  class="text-[10px] bg-white border border-[#ededed] rounded-[4px] px-1.5 py-0.5 text-audyr-ink focus:outline-none focus:border-audyr-ink cursor-pointer font-semibold"
                  title="Ubah peran pengguna"
                >
                  <option value="TRIAL">TRIAL</option>
                  <option value="PREMIUM">PREMIUM</option>
                  <option value="REVIEWER">REVIEWER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>
            </td>
            <td class="py-3.5 px-4 font-extrabold text-sm text-audyr-ink tabular-nums">
              <div class="flex items-center space-x-2">
                <span>{{ user.token_balance }}</span>
                <button
                  type="button"
                  @click="emit('adjustTokens', user.id, 5)"
                  class="text-[10px] bg-transparent border border-[#ededed] hover:bg-[#ededed] text-audyr-ink px-1.5 py-0.5 rounded-[4px] font-bold transition-colors"
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
            <td class="py-3.5 px-5 text-right whitespace-nowrap space-x-1.5">
              <button
                type="button"
                @click="openEdit(user)"
                class="text-xs font-semibold px-2 py-1 rounded-[4px] border border-[#ededed] text-audyr-ink hover:bg-[#ededed] transition-colors tracking-tight"
                title="Edit data pengguna"
              >
                Edit
              </button>
              <button
                type="button"
                @click="emit('toggleStatus', user.id)"
                class="text-xs font-bold px-2 py-1 rounded-[4px] border transition-colors tracking-tight"
                :class="user.is_active ? 'text-red-600 border-red-200 hover:bg-red-50' : 'text-[#065f46] border-[#a7f3d0] hover:bg-audyr-mint-whisper'"
              >
                {{ user.is_active ? 'Suspend' : 'Aktifkan' }}
              </button>
              <button
                type="button"
                @click="confirmDelete(user)"
                class="text-xs font-bold px-2 py-1 rounded-[4px] border border-red-200 text-red-600 hover:bg-red-50 transition-colors tracking-tight"
                title="Hapus akun pengguna"
              >
                Hapus
              </button>
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
