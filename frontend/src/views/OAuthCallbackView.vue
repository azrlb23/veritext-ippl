<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { getHomeRouteForRole } from "../utils/navigation";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isProcessing = ref(true);
const errorMessage = ref("");

onMounted(async () => {
  const code = route.query.code as string;
  const oauthError = route.query.oauth_error as string;

  if (oauthError) {
    isProcessing.value = false;
    errorMessage.value = decodeURIComponent(oauthError);
    return;
  }

  if (!code) {
    isProcessing.value = false;
    errorMessage.value = "Kode otentikasi Google tidak ditemukan.";
    return;
  }

  try {
    await authStore.exchangeGoogleCode(code);

    if (!authStore.user) {
      authStore.clearLocalSession();
      isProcessing.value = false;
      errorMessage.value = "Gagal memuat profil pengguna. Silakan coba masuk kembali.";
      return;
    }

    authStore.markWelcome();
    router.replace(getHomeRouteForRole(authStore.role));
  } catch (err: any) {
    authStore.clearLocalSession();
    isProcessing.value = false;
    errorMessage.value = err?.response?.data?.detail || err?.message || "Gagal memproses sesi login Google.";
  }
});
</script>

<template>
  <AuthCard
    title="Menghubungkan akun"
    :subtitle="isProcessing ? 'Menyiapkan sesi aman dan kredensial akun Google Anda.' : 'Autentikasi Google belum berhasil diproses.'"
  >
    <div v-if="isProcessing" class="flex items-center gap-4 py-4" role="status">
      <svg class="h-9 w-9 shrink-0 animate-spin motion-reduce:animate-none" viewBox="0 0 36 36" fill="none" aria-hidden="true">
        <circle cx="18" cy="18" r="15" stroke="#D5ECE8" stroke-width="4" />
        <path d="M18 3 a15 15 0 0 1 15 15" stroke="#0F766E" stroke-width="4" stroke-linecap="round" />
      </svg>
      <p class="text-[14.5px] leading-[1.6] text-[#4B4757]">Memverifikasi sesi Google...</p>
    </div>

    <div v-else class="space-y-5">
      <p role="alert" class="text-[14.5px] leading-[1.65] text-[#B91C1C]">
        {{ errorMessage || "Terjadi kesalahan saat memproses login Google." }}
      </p>
      <router-link
        to="/login"
        class="vt-btn-dark inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold"
      >
        Kembali ke halaman masuk
      </router-link>
    </div>
  </AuthCard>
</template>
