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
const joinedLabel = computed(() => {
  const raw = authStore.user?.created_at;
  if (!raw) return "-";
  const d = new Date(raw);
  return Number.isNaN(d.getTime()) ? "-" : d.toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" });
});
const aiQuotaLabel = computed(() =>
  authStore.role === "FREE" ? `${authStore.user?.ai_trial_remaining ?? 3} percobaan` : "Penuh"
);
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
    <dl class="mt-6 grid grid-cols-1 gap-4 border-y border-[#E8ECEB] py-5 sm:grid-cols-2">
      <div class="min-w-0">
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Email</dt>
        <dd class="mt-1 truncate text-[15px] font-semibold text-[#14111C]">{{ authStore.user?.email }}</dd>
      </div>
      <div>
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Paket</dt>
        <dd class="mt-1 text-[15px] font-semibold text-[#14111C]">{{ planLabel }}</dd>
      </div>
      <div>
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Bergabung</dt>
        <dd class="mt-1 text-[15px] font-semibold text-[#14111C]">{{ joinedLabel }}</dd>
      </div>
      <div>
        <dt class="text-[13px] font-medium text-[#5E5A6B]">Sisa kuota AI</dt>
        <dd class="mt-1 text-[15px] font-semibold text-[#14111C]">{{ aiQuotaLabel }}</dd>
      </div>
    </dl>
    <form class="mt-7 space-y-7" @submit.prevent="save">
      <AuthField id="akun-nama" v-model="name" label="Nama lengkap" autocomplete="name" />
      <button
        type="submit"
        :disabled="!dirty || saving"
        class="vt-btn-dark inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full px-8 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >{{ saving ? "Menyimpan..." : "Simpan nama" }}</button>
    </form>
  </section>
</template>
