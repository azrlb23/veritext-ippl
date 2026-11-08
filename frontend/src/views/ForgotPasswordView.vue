<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import AuthField from "../components/auth/AuthField.vue";
import { authService } from "../services/authService";

const router = useRouter();
const email = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");
const devResetUrl = ref<string | null>(null);

function validateEmail(val: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
}

async function handleSubmit() {
  errorMessage.value = "";
  devResetUrl.value = null;
  if (!email.value.trim() || !validateEmail(email.value.trim())) {
    errorMessage.value = "Silakan masukkan alamat email yang valid.";
    return;
  }
  isLoading.value = true;
  try {
    const res: any = await authService.forgotPassword(email.value.trim());
    isSuccess.value = true;
    if (res?.data?.reset_url) devResetUrl.value = res.data.reset_url;
  } catch (err: any) {
    if (err?.response?.status === 404) errorMessage.value = "Jika email terdaftar, tautan pemulihan telah dikirim.";
    else if (err?.response?.status === 429) errorMessage.value = "Terlalu sering meminta tautan. Tunggu 5 menit.";
    else errorMessage.value = err?.response?.data?.detail || "Gagal mengirimkan permintaan.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard eyebrow="Pemulihan akun" title="Lupa kata sandi" :subtitle="['Masukkan alamat email terdaftar. Kami kirim tautan', 'pemulihan yang berlaku 15 menit.']">
    <div v-if="isSuccess" class="space-y-5">
      <div class="rounded-[22px] bg-[#F3EEFA] p-5 text-[14.5px] leading-[1.65] text-[#4B4757]">
        <div class="text-[17px] font-semibold text-[#15803D]">Tautan pemulihan dikirim</div>
        <p class="mt-1.5">Kami mengirim tautan pemulihan ke <strong class="font-semibold text-[#14111C]">{{ email }}</strong>. Periksa kotak masuk atau spam.</p>
      </div>

      <div v-if="devResetUrl" class="space-y-3 rounded-[22px] bg-[#F3EEFA] p-5">
        <div class="text-[13.5px] font-semibold text-[#6D28D9]">Mode pengujian lokal</div>
        <p class="text-[14px] leading-[1.6] text-[#4B4757]">Tautan aktif. Buka formulir kata sandi baru:</p>
        <router-link :to="devResetUrl.replace(/^https?:\/\/[^\/]+/, '')" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0">Setel ulang kata sandi</router-link>
      </div>

      <router-link to="/login" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#F3EEFA] px-6 text-[15px] font-semibold text-[#14111C] transition-colors duration-200 hover:bg-[#EBE3F6]">Kembali ke halaman masuk</router-link>
    </div>

    <form v-else class="space-y-6" @submit.prevent="handleSubmit">
      <p v-if="errorMessage" role="alert" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
        <span>{{ errorMessage }}</span>
        <button type="button" class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none transition-colors hover:bg-[#14111C]/[0.05]" aria-label="Tutup pesan" @click="errorMessage = ''">&times;</button>
      </p>
      <AuthField id="forgot-email" v-model="email" label="Alamat email" type="email" autocomplete="email" placeholder="nama@email.com" :disabled="isLoading" />

      <div class="flex flex-col-reverse gap-3 sm:flex-row sm:items-center">
        <button type="button" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#F3EEFA] px-6 text-[15px] font-semibold text-[#14111C] transition-colors duration-200 hover:bg-[#EBE3F6] sm:flex-1" @click="router.push('/login')">Kembali</button>
        <button type="submit" :disabled="isLoading" class="inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full bg-[#14111C] px-6 text-[15px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0 sm:flex-1">{{ isLoading ? 'Mengirim...' : 'Kirim tautan' }}</button>
      </div>
    </form>
  </AuthCard>
</template>
