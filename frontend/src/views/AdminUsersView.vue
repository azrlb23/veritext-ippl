<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useAdminData, useSectionReveal } from "../composables";
import { UserTable } from "../components/admin";

const { sectionRef, isVisible } = useSectionReveal({ threshold: 0.06, rootMargin: "0px" });
const { loading, error, users, usersMeta, fetchUsers } = useAdminData();

const search = ref("");
const selectedRole = ref("");
const page = ref(1);
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

function loadUsers() {
  void fetchUsers({ q: search.value, role: selectedRole.value, page: page.value });
}

function handleSearch(value: string) {
  search.value = value;
  page.value = 1;
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadUsers, 300);
}

function handleRole(role: string) {
  selectedRole.value = role;
  page.value = 1;
  loadUsers();
}

function handlePage(nextPage: number) {
  page.value = nextPage;
  loadUsers();
}

onMounted(loadUsers);
onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer);
});
</script>

<template>
  <div ref="sectionRef" class="vt-section mx-auto max-w-[1180px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7" :class="{ 'is-visible': isVisible }">
    <div class="vt-reveal mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Daftar pengguna terdaftar.
      </h1>
      <button type="button" :disabled="loading" class="vt-btn-light inline-flex h-12 cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] disabled:opacity-50" @click="loadUsers">
        {{ loading ? "Memuat..." : "Muat ulang" }}
      </button>
    </div>

    <div v-if="error && !loading" class="vt-reveal mb-6 flex flex-col gap-3 rounded-[28px] bg-white p-6 shadow-float sm:flex-row sm:items-center sm:justify-between" role="alert">
      <p class="text-[15px] font-medium text-[#B91C1C]">{{ error }}</p>
      <button type="button" class="vt-btn-dark inline-flex h-11 cursor-pointer items-center justify-center rounded-full px-6 text-[14px] font-semibold" @click="loadUsers">Coba lagi</button>
    </div>

    <div class="vt-reveal vt-d-1">
      <UserTable
        :users="users"
        :loading="loading"
        :page="usersMeta.page"
        :pages="usersMeta.pages"
        :total="usersMeta.total"
        :search="search"
        :selected-role="selectedRole"
        @update:search="handleSearch"
        @update:selected-role="handleRole"
        @change-page="handlePage"
      />
    </div>
  </div>
</template>
