<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import { useAuthStore } from "../stores/auth";
import { useNotification } from "../composables";
import { getHomeRouteForRole } from "../utils/navigation";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { showNotification } = useNotification();

const ticket = ref("");
const email = ref("");
const fullName = ref("");
const password = ref("");
const confirmPassword = ref("");
const showPassword = ref(false);
const agreePDP = ref(true);
const isLoading = ref(false);
const errorMessage = ref("");
const isTicketInvalid = ref(false);
const ticketErrorMessage = ref("");

function decodeTicketPayload(token: string): Record<string, any> | null {
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const jsonStr = decodeURIComponent(
      atob(base64).split("").map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2)).join("")
    );
    return JSON.parse(jsonStr);
  } catch {
    return null;
  }
}

onMounted(() => {
  const queryTicket = (route.query.ticket as string) || "";
  if (!queryTicket) {
    isTicketInvalid.value = true;
    ticketErrorMessage.value = "Tiket pendaftaran Google tidak ditemukan.";
    return;
  }
  ticket.value = queryTicket;
  const payload = decodeTicketPayload(queryTicket);
  if (!payload || !payload.email) {
    isTicketInvalid.value = true;
    ticketErrorMessage.value = "Tiket pendaftaran tidak valid atau telah kedaluwarsa.";
    return;
  }
  email.value = payload.email || "";
  fullName.value = payload.name || payload.full_name || (payload.email ? payload.email.split("@")[0] : "");
});

const isPassValid = computed(() => password.value.length >= 8 && /[A-Z]/.test(password.value) && /[0-9]/.test(password.value));
const isFormValid = computed(() => fullName.value.trim().length >= 2 && isPassValid.value && password.value === confirmPassword.value && agreePDP.value && !isLoading.value);

async function handleSubmit() {
  errorMessage.value = "";
  if (!isFormValid.value || !ticket.value) return;
  isLoading.value = true;
  try {
    await authStore.completeGoogleSignup({ ticket: ticket.value, full_name: fullName.value.trim(), password: password.value });
    showNotification("Profil berhasil disimpan. Selamat datang!", "success");
    router.replace(getHomeRouteForRole(authStore.role));
  } catch (err: any) {
    const status = err?.response?.status;
    if (status === 401 || status === 409) {
      isTicketInvalid.value = true;
      ticketErrorMessage.value = err?.response?.data?.detail || "Tiket pendaftaran telah kedaluwarsa atau tidak valid.";
    } else {
      errorMessage.value = err?.response?.data?.detail || err?.message || "Gagal menyimpan data akun.";
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard eyebrow="ONBOARDING PENGGUNA" title="Lengkapi Akun Anda" subtitle="Verifikasi identitas resmi Anda dan amankan akun dengan kata sandi pribadi.">
    <div class="space-y-4 font-sans text-xs">
      <div v-if="isTicketInvalid" class="space-y-4 py-2">
        <div class="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 space-y-1">
          <p class="font-semibold">Tiket Tidak Valid</p>
          <p class="text-[11px]">{{ ticketErrorMessage }}</p>
        </div>
        <router-link to="/register" class="block w-full py-2.5 text-center rounded-full text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-all">
          Kembali ke Pendaftaran
        </router-link>
      </div>

      <div v-else>
        <div v-if="errorMessage" class="mb-3 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 flex justify-between">
          <span>{{ errorMessage }}</span>
          <button type="button" @click="errorMessage = ''" class="font-bold">&times;</button>
        </div>

        <div class="mb-3 p-3 bg-slate-100 border border-slate-200 rounded-xl flex items-center justify-between">
          <div>
            <p class="text-[10px] font-semibold text-slate-500 uppercase">Terhubung via Google</p>
            <p class="text-xs font-semibold text-slate-900 truncate max-w-[200px]">{{ email || "Akun Google" }}</p>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">Terverifikasi</span>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-3">
          <div class="space-y-1">
            <label class="block font-semibold text-slate-900">Nama Lengkap Resmi <span class="text-red-500">*</span></label>
            <input v-model="fullName" type="text" required placeholder="Nama Lengkap Resmi" class="w-full text-xs font-medium text-slate-900 bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-blue-600 focus:bg-white" />
          </div>

          <div class="space-y-1">
            <div class="flex justify-between items-center">
              <label class="block font-semibold text-slate-900">Kata Sandi Baru <span class="text-red-500">*</span></label>
              <button type="button" @click="showPassword = !showPassword" class="text-[11px] text-slate-500 hover:text-slate-900">{{ showPassword ? "Tutup" : "Lihat" }}</button>
            </div>
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="Minimal 8 karakter (huruf besar & angka)" class="w-full text-xs font-medium text-slate-900 bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-blue-600 focus:bg-white" />
          </div>

          <div class="space-y-1">
            <label class="block font-semibold text-slate-900">Konfirmasi Kata Sandi <span class="text-red-500">*</span></label>
            <input v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" required placeholder="Ulangi kata sandi" class="w-full text-xs font-medium text-slate-900 bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-blue-600 focus:bg-white" />
            <p v-if="confirmPassword && password !== confirmPassword" class="text-[10px] text-red-600">Kata sandi belum cocok.</p>
          </div>

          <label class="flex items-start gap-2 pt-1 cursor-pointer">
            <input type="checkbox" v-model="agreePDP" class="mt-0.5 rounded text-blue-600" />
            <span class="text-[11px] text-slate-600">Setujui pemrosesan data identitas Anda untuk pembuatan akun.</span>
          </label>

          <button type="submit" :disabled="!isFormValid" class="w-full py-2.5 rounded-full text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer shadow-sm">
            {{ isLoading ? "Menyimpan..." : "Simpan & Masuk ke Beranda" }}
          </button>
        </form>
      </div>
    </div>
  </AuthCard>
</template>
