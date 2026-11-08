<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { AuthCard } from "../components/auth";
import { authService } from "../services/authService";

const router = useRouter();
const email = ref("");
const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");
const isFocused = ref(false);
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
  <AuthCard eyebrow="PEMULIHAN AKUN" title="Lupa kata sandi" :subtitle="['Masukkan alamat email terdaftar. Kami kirim tautan', 'pemulihan yang berlaku 15 menit.']">
    <div v-if="isSuccess" class="space-y-4 pt-1 font-sans">
      <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs space-y-1">
        <div class="font-bold text-sm">Tautan Pemulihan Dikirim</div>
        <p class="text-slate-600 leading-relaxed">Tautan pemulihan kata sandi telah dikirim ke <strong>{{ email }}</strong>. Periksa kotak masuk atau spam.</p>
      </div>

      <div v-if="devResetUrl" class="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-blue-600 uppercase">Mode Pengujian Lokal</span>
          <span class="text-[10px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-semibold">Tautan Aktif</span>
        </div>
        <p class="text-xs text-slate-500">Klik tombol di bawah untuk membuka formulir pembuatan kata sandi baru:</p>
        <router-link :to="devResetUrl.replace(/^https?:\/\/[^\/]+/, '')" class="w-full h-10 flex items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold cursor-pointer">
          Setel Ulang Kata Sandi &rarr;
        </router-link>
      </div>

      <router-link to="/login" class="w-full h-10 flex items-center justify-center rounded-full bg-white hover:bg-slate-50 text-slate-900 text-xs font-semibold border border-slate-300">
        Kembali ke Halaman Masuk
      </router-link>
    </div>

    <div v-else class="space-y-4 font-sans">
      <div v-if="errorMessage" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex justify-between">
        <span>{{ errorMessage }}</span>
        <button type="button" @click="errorMessage = ''" class="text-red-500 font-bold ml-2">&times;</button>
      </div>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div class="w-full h-14 rounded-xl bg-slate-100 px-4 pt-1.5 pb-1 flex flex-col justify-between relative">
          <label for="forgot-email" class="text-[11px] font-medium" :class="isFocused ? 'text-blue-600' : 'text-slate-500'">Alamat email</label>
          <input id="forgot-email" v-model="email" type="email" required autocomplete="email" placeholder="nama@email.com" :disabled="isLoading" @focus="isFocused = true" @blur="isFocused = false" class="w-full bg-transparent text-sm font-medium text-slate-900 focus:outline-none" />
          <div v-if="isFocused || email" class="absolute bottom-1 left-4 right-4 h-0.5 rounded-full bg-blue-600"></div>
        </div>

        <div class="flex items-center justify-between gap-3 pt-1">
          <button type="button" @click="router.push('/login')" class="flex-1 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900 text-sm font-semibold transition-all">Kembali</button>
          <button type="submit" :disabled="isLoading" class="flex-1 sm:max-w-[160px] h-11 rounded-full bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold transition-all disabled:opacity-50">
            {{ isLoading ? 'Mengirim...' : 'Kirim tautan' }}
          </button>
        </div>
      </form>
    </div>
  </AuthCard>
</template>
