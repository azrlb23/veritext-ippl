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
const open = ref(false);
const typed = ref("");
const busy = ref(false);
const confirmed = computed(() => typed.value.trim().toUpperCase() === "HAPUS");

async function removeAccount() {
  busy.value = true;
  try {
    await authService.deleteAccount();
    await authStore.logout();
    showNotification("Akun dan seluruh naskah Anda sudah dihapus.", "info");
    router.push("/");
  } catch (err: any) {
    showNotification(err?.response?.data?.detail || "Akun belum bisa dihapus.", "error");
    busy.value = false;
  }
}
</script>

<template>
  <section class="rounded-[32px] bg-white p-7 shadow-float sm:p-9" aria-labelledby="hapus-judul">
    <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
      <div class="max-w-xl">
        <h2 id="hapus-judul" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Hapus akun</h2>
        <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">
          Akun, seluruh naskah, laporan, dan percakapan asisten dihapus permanen. Sisa token tidak dapat dikembalikan.
        </p>
      </div>
      <button
        type="button"
        class="inline-flex h-12 flex-shrink-0 cursor-pointer items-center justify-center rounded-full bg-[#FEE2E2] px-7 text-[15px] font-semibold text-[#B91C1C] transition-colors hover:bg-[#FECACA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
        @click="open = true"
      >Hapus akun saya</button>
    </div>

    <div v-if="open" class="fixed inset-0 z-[60] flex items-end justify-center bg-[#14111C]/20 p-4 backdrop-blur-[2px] sm:items-center" @click.self="open = false">
      <div class="w-full max-w-md rounded-[32px] bg-white p-7 shadow-float" role="dialog" aria-modal="true" aria-labelledby="hapus-konfirmasi">
        <h3 id="hapus-konfirmasi" class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Yakin menghapus akun?</h3>
        <p class="mt-2 text-[15px] leading-relaxed text-[#4B4757]">Tindakan ini tidak bisa dibatalkan. Ketik HAPUS untuk melanjutkan.</p>
        <div class="mt-6"><AuthField id="hapus-ketik" v-model="typed" label="Ketik HAPUS" /></div>
        <div class="mt-7 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button type="button" class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-white px-6 text-[15px] font-semibold text-[#14111C] shadow-lift" @click="open = false">Batal</button>
          <button
            type="button"
            :disabled="!confirmed || busy"
            class="inline-flex h-12 cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark disabled:cursor-not-allowed disabled:opacity-40"
            @click="removeAccount"
          >{{ busy ? "Menghapus..." : "Hapus permanen" }}</button>
        </div>
      </div>
    </div>
  </section>
</template>
