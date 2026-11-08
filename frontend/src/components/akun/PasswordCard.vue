<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import AuthField from "../auth/AuthField.vue";
import { authService } from "../../services/authService";
import { useAuthStore } from "../../stores/auth";
import { useNotification } from "../../composables/useNotification";

const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();
const oldPassword = ref("");
const newPassword = ref("");
const confirm = ref("");
const saving = ref(false);

const tooShort = computed(() => newPassword.value.length > 0 && newPassword.value.length < 8);
const mismatch = computed(() => confirm.value.length > 0 && confirm.value !== newPassword.value);
const ready = computed(() => oldPassword.value && newPassword.value.length >= 8 && confirm.value === newPassword.value);

async function submit() {
  saving.value = true;
  try {
    await authService.changePassword(oldPassword.value, newPassword.value);
    showNotification("Kata sandi diganti. Silakan masuk kembali.", "success");
    await authStore.logout();
    router.push("/login");
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Kata sandi belum bisa diganti.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="sandi-judul">
    <h2 id="sandi-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Kata sandi</h2>
    <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">Setelah diganti, semua perangkat akan keluar dan Anda perlu masuk lagi.</p>
    <form class="mt-7 space-y-7" @submit.prevent="submit">
      <AuthField id="sandi-lama" v-model="oldPassword" type="password" label="Kata sandi saat ini" autocomplete="current-password" revealable />
      <AuthField id="sandi-baru" v-model="newPassword" type="password" label="Kata sandi baru (minimal 8 karakter)" autocomplete="new-password" :invalid="tooShort" revealable />
      <AuthField id="sandi-ulang" v-model="confirm" type="password" label="Ulangi kata sandi baru" autocomplete="new-password" :invalid="mismatch" />
      <p v-if="mismatch" class="-mt-3 text-[14px] text-[#B91C1C]">Kata sandi belum sama.</p>
      <button
        type="submit"
        :disabled="!ready || saving"
        class="inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-8 text-[15px] font-semibold text-white shadow-btn-dark transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >{{ saving ? "Menyimpan..." : "Ganti kata sandi" }}</button>
    </form>
  </section>
</template>
