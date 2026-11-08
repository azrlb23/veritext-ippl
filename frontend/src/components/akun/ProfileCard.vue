<script setup lang="ts">
import { computed, ref } from "vue";
import AuthField from "../auth/AuthField.vue";
import { authService } from "../../services/authService";
import { useAuthStore } from "../../stores/auth";
import { useNotification } from "../../composables/useNotification";

const authStore = useAuthStore();
const { showNotification } = useNotification();
const name = ref(authStore.user?.full_name || "");
const saving = ref(false);

const planLabel = computed(() => (authStore.role === "PREMIUM" ? "Premium" : authStore.role === "ADMIN" ? "Administrator" : "Gratis"));
const dirty = computed(() => name.value.trim().length >= 2 && name.value.trim() !== (authStore.user?.full_name || ""));

async function save() {
  saving.value = true;
  try {
    await authService.updateProfile(name.value.trim());
    await authStore.fetchProfile();
    showNotification("Nama Anda sudah diperbarui.", "success");
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Nama belum bisa disimpan.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="profil-judul">
    <h2 id="profil-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Profil</h2>
    <dl class="mt-6 grid grid-cols-2 gap-4 rounded-[24px] bg-[#F3EEFA] p-5">
      <div class="min-w-0">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Email</dt>
        <dd class="mt-1 truncate text-[15px] font-semibold text-[#14111C]">{{ authStore.user?.email }}</dd>
      </div>
      <div>
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Paket</dt>
        <dd class="mt-1 text-[15px] font-semibold text-[#14111C]">{{ planLabel }}</dd>
      </div>
    </dl>
    <form class="mt-7 space-y-7" @submit.prevent="save">
      <AuthField id="akun-nama" v-model="name" label="Nama lengkap" autocomplete="name" />
      <button
        type="submit"
        :disabled="!dirty || saving"
        class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >{{ saving ? "Menyimpan..." : "Simpan nama" }}</button>
    </form>
  </section>
</template>
