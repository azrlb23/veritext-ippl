<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import AuthField from "../components/auth/AuthField.vue";
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
  <AuthCard eyebrow="Lengkapi akun" title="Lengkapi akun Anda" subtitle="Verifikasi identitas Anda dan amankan akun dengan kata sandi pribadi.">
    <div v-if="isTicketInvalid" class="space-y-5">
      <div class="space-y-1 text-[14.5px] leading-[1.65]">
        <p class="font-semibold text-[#B91C1C]">Tiket tidak valid</p>
        <p class="text-[#4B4757]">{{ ticketErrorMessage }}</p>
      </div>
      <router-link to="/register" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">Kembali ke pendaftaran</router-link>
    </div>

    <form v-else class="space-y-6" @submit.prevent="handleSubmit">
      <p v-if="errorMessage" role="alert" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
        <span>{{ errorMessage }}</span>
        <button type="button" class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none transition-colors hover:bg-[#14111C]/[0.05]" aria-label="Tutup pesan" @click="errorMessage = ''">&times;</button>
      </p>
      <div class="rounded-[20px] bg-[#F3EEFA] px-5 py-4">
        <p class="text-[12.5px] font-medium text-[#5E5A6B]">Terhubung lewat Google</p>
        <p class="mt-0.5 truncate text-[15px] font-semibold text-[#14111C]">{{ email || "Akun Google" }}</p>
      </div>

      <AuthField id="onb-name" v-model="fullName" label="Nama lengkap" autocomplete="name" placeholder="Nama lengkap resmi" />
      <AuthField id="onb-pass" v-model="password" label="Kata sandi baru" type="password" revealable autocomplete="new-password" placeholder="Minimal 8 karakter, huruf besar dan angka" />
      <AuthField id="onb-conf" v-model="confirmPassword" label="Konfirmasi kata sandi" type="password" revealable autocomplete="new-password" placeholder="Ulangi kata sandi" :invalid="confirmPassword.length > 0 && password !== confirmPassword" />
      <p v-if="confirmPassword && password !== confirmPassword" class="-mt-3 text-[13px] font-medium text-[#B91C1C]">Kata sandi belum cocok.</p>

      <label class="flex min-h-[44px] cursor-pointer select-none items-center space-x-2.5 text-[13.5px] leading-tight text-[#4B4757]">
        <input v-model="agreePDP" type="checkbox" class="h-[18px] w-[18px] shrink-0 rounded accent-[#8A3FE0]" />
        <span>Setujui pemrosesan data identitas Anda untuk pembuatan akun.</span>
      </label>

      <button type="submit" :disabled="!isFormValid" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">{{ isLoading ? "Menyimpan..." : "Simpan dan masuk" }}</button>
    </form>
  </AuthCard>
</template>
