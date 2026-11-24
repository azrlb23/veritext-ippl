<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import AuthField from "../components/auth/AuthField.vue";
import GoogleAuthButton from "../components/auth/GoogleAuthButton.vue";
import { authService } from "../services/authService";
import { readableDetail } from "../utils/errorMessage";

const router = useRouter();
const email = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");

function validateEmail(val: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
}

function handleGoogleReset() {
  window.location.href = "/api/v1/auth/google/login?intent=reset";
}

async function handleSubmit() {
  errorMessage.value = "";
  const cleanEmail = email.value.trim();
  if (!cleanEmail || !validateEmail(cleanEmail)) {
    errorMessage.value = "Silakan masukkan alamat email yang valid.";
    return;
  }
  isLoading.value = true;
  try {
    await authService.forgotPassword(cleanEmail);
    email.value = cleanEmail;
    isSuccess.value = true;
  } catch (err: any) {
    if (err?.response?.status === 404) {
      errorMessage.value = "Jika email terdaftar, kode OTP dan tautan pemulihan telah dikirim.";
    } else if (err?.response?.status === 429) {
      errorMessage.value = "Terlalu sering meminta pemulihan. Tunggu 5 menit.";
    } else {
      errorMessage.value = readableDetail(err?.response?.data?.detail, "Gagal mengirimkan permintaan.");
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <AuthCard
    title="Lupa kata sandi"
    :subtitle="['Masukkan email terdaftar untuk menerima kode OTP', '6-digit dan tautan pemulihan yang berlaku 1 jam.']"
  >
    <div v-if="isSuccess" class="space-y-5">
      <div class="border-b border-[#E8ECEB] pb-5 text-[14.5px] leading-[1.65] text-[#4B4757]">
        <div class="text-[16px] font-semibold text-[#0F766E]">Kode OTP dan tautan dikirim</div>
        <p class="mt-1.5">
          Kami mengirim kode OTP 6-digit dan tautan pemulihan ke
          <strong class="font-semibold text-[#14111C]">{{ email }}</strong>. Periksa kotak masuk atau folder spam Anda.
        </p>
      </div>

      <div class="flex flex-col gap-3">
        <router-link
          :to="{ path: '/reset-password', query: { email: email.trim() } }"
          class="vt-btn-dark inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold"
        >
          Masukkan kode OTP
        </router-link>
        <router-link
          to="/login"
          class="vt-btn-light inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold"
        >
          Kembali ke halaman masuk
        </router-link>
      </div>
    </div>

    <form v-else class="space-y-6" @submit.prevent="handleSubmit">
      <p v-if="errorMessage" role="alert" class="flex items-start justify-between gap-2 text-[14px] leading-[1.6] text-[#B91C1C]">
        <span>{{ errorMessage }}</span>
        <button
          type="button"
          class="-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-[20px] leading-none transition-colors hover:bg-[#14111C]/[0.05]"
          aria-label="Tutup pesan"
          @click="errorMessage = ''"
        >&times;</button>
      </p>

      <AuthField
        id="forgot-email"
        v-model="email"
        label="Alamat email"
        type="email"
        autocomplete="email"
        placeholder="nama@email.com"
        :disabled="isLoading"
      />

      <div class="flex flex-col-reverse gap-3 sm:flex-row sm:items-center">
        <button
          type="button"
          class="vt-btn-light inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold sm:flex-1"
          @click="router.push('/login')"
        >
          Kembali
        </button>
        <button
          type="submit"
          :disabled="isLoading"
          class="vt-btn-dark inline-flex h-[52px] w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold disabled:cursor-not-allowed disabled:opacity-50 sm:flex-1"
        >
          {{ isLoading ? "Mengirim..." : "Kirim OTP & tautan" }}
        </button>
      </div>

      <div class="flex items-center gap-3 text-[13px] text-[#5E5A6B]">
        <span class="h-px flex-1 bg-[#E8ECEB]"></span>
        <span>atau</span>
        <span class="h-px flex-1 bg-[#E8ECEB]"></span>
      </div>

      <GoogleAuthButton text="Pulihkan dengan Google" :disabled="isLoading" @click="handleGoogleReset" />
    </form>
  </AuthCard>
</template>
