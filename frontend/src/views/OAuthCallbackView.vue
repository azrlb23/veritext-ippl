<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";
import { getHomeRouteForRole } from "../utils/navigation";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const isProcessing = ref(true);
const errorMessage = ref("");

onMounted(async () => {
  const token = route.query.token as string;
  const oauthError = route.query.oauth_error as string;

  if (oauthError) {
    isProcessing.value = false;
    errorMessage.value = decodeURIComponent(oauthError);
    return;
  }

  if (!token) {
    isProcessing.value = false;
    errorMessage.value = "Token otentikasi Google tidak ditemukan.";
    return;
  }

  try {
    localStorage.setItem("veritext_access_token", token);
    (authStore as any).token = token;

    await authStore.fetchProfile();

    if (!authStore.user) {
      await authStore.logout();
      isProcessing.value = false;
      errorMessage.value = "Gagal memuat profil pengguna. Silakan coba masuk kembali.";
      return;
    }

    authStore.markWelcome();

    showNotification(
      "Selamat datang kembali! Berhasil masuk dengan akun Google.",
      "success",
      "Login Berhasil"
    );

    router.replace(getHomeRouteForRole(authStore.role));
  } catch (err: any) {
    await authStore.logout();
    isProcessing.value = false;
    errorMessage.value =
      err?.response?.data?.detail ||
      err?.message ||
      "Gagal memproses sesi login Google.";
  }
});
</script>

<template>
  <div class="relative min-h-screen bg-gradient-to-br from-[#E8F0FF] via-[#DDF4FF] to-[#EDE7FF] flex items-center justify-center p-4 font-sans select-none overflow-hidden">
    <div class="absolute inset-0 pointer-events-none overflow-hidden -z-10" aria-hidden="true">
      <div class="absolute -top-32 right-10 w-96 h-96 rounded-full bg-[#3B82F6]/30 blur-[100px]"></div>
      <div class="absolute top-[400px] -left-20 w-[450px] h-[450px] rounded-full bg-[#22D3EE]/25 blur-[120px]"></div>
    </div>

    <div class="w-full max-w-md bg-white rounded-[32px] border border-white/80 shadow-[0_16px_48px_rgba(138,152,184,0.18)] p-8 text-center space-y-6">
      <div v-if="isProcessing" class="space-y-4 py-4">
        <div class="w-12 h-12 rounded-full border-3 border-[#1560BD] border-t-transparent animate-spin mx-auto"></div>
        <div class="space-y-1">
          <h3 class="text-base font-bold text-[#0B0F19]">Menghubungkan Akun Google...</h3>
          <p class="text-xs text-[#5B6475]">Menyiapkan sesi aman dan kredensial akun Anda.</p>
        </div>
      </div>

      <div v-else class="space-y-4 py-2">
        <div class="w-12 h-12 rounded-full bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center mx-auto text-[#B91C1C]">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="space-y-1">
          <h3 class="text-base font-bold text-[#0B0F19]">Autentikasi Google Gagal</h3>
          <p class="text-xs text-[#5B6475] leading-relaxed max-w-xs mx-auto">
            {{ errorMessage || "Terjadi kesalahan saat memproses login Google." }}
          </p>
        </div>
        <div class="pt-2">
          <router-link
            to="/login"
            class="inline-flex items-center px-6 py-2.5 bg-[#1560BD] hover:bg-[#1A73D9] text-white text-xs font-semibold rounded-full shadow-xs transition-all"
          >
            Kembali ke Halaman Masuk
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
