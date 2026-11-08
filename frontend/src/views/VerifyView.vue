<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useNotification } from "../composables";
import { auditService } from "../services/auditService";
import { VerifySearchBox, CertificateDetailsCard, VerifyHowItWorks, type CertificateDetails } from "../components/verify";

const route = useRoute();
const router = useRouter();
const { showNotification } = useNotification();

const isValid = ref(false);
const isChecking = ref(false);
const certDetails = ref<CertificateDetails>({
  uuid: "", title: "", examiner: "", auditDate: "",
  compositeScore: 0, lexicalScore: 0, semanticScore: 0, styloScore: 0,
});

async function handleLookup(targetUuid: string) {
  const clean = targetUuid?.trim();
  if (!clean || clean === "sample" || clean === "invalid") {
    certDetails.value.uuid = "";
    isValid.value = false;
    return;
  }
  isChecking.value = true;
  try {
    const res = await auditService.verifyCertificate(clean);
    isValid.value = Boolean(res?.is_valid);
    certDetails.value = {
      uuid: clean,
      title: res?.title || "Naskah Terverifikasi",
      examiner: res?.examiner_name || "Peneliti Terdaftar",
      auditDate: res?.audit_date || new Date().toLocaleDateString("id-ID"),
      compositeScore: res?.score_composite ?? 0,
      lexicalScore: res?.score_lexical ?? 0,
      semanticScore: res?.score_semantic ?? 0,
      styloScore: res?.score_stylometric ?? 0,
    };
    if (res?.is_valid) showNotification("Sertifikat berhasil divalidasi.", "success");
    else showNotification(res?.message || "Kode sertifikat tidak ditemukan.", "error");
    if (route.params.uuid !== clean) router.replace(`/verify/${clean}`);
  } catch {
    isValid.value = false;
    certDetails.value.uuid = clean;
    showNotification("Kode sertifikat tidak ditemukan atau tidak valid.", "error");
  } finally {
    isChecking.value = false;
  }
}

function resetVerification() {
  certDetails.value.uuid = "";
  isValid.value = false;
  router.replace("/verify");
}

function copyValidationLink() {
  navigator.clipboard?.writeText(window.location.href);
  showNotification("Tautan validasi sertifikat berhasil disalin.", "success");
}

onMounted(() => {
  const p = route.params.uuid as string;
  if (p && p.trim() && p !== "sample" && p !== "invalid") void handleLookup(p);
});

watch(() => route.params.uuid, (n) => {
  if (n && typeof n === "string" && n !== certDetails.value.uuid && n !== "sample") void handleLookup(n);
});
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 font-sans">
    <!-- Header -->
    <div class="space-y-2">
      <span class="text-[11px] font-bold text-[#1560BD] bg-[#EAF3FE] border border-[#BFDBFE] px-3 py-1 rounded-full uppercase tracking-wider">
        Verifikasi Sertifikat Resmi - Publik
      </span>
      <h1 class="text-2xl sm:text-3xl font-bold text-[#0B0F19] tracking-tight">Verifikasi Keaslian Sertifikat &amp; Naskah</h1>
      <p class="text-xs sm:text-sm text-[#5B6475]">
        Validasi keaslian laporan audit berbasis kode UUID verifikasi resmi dan pencatatan berkas dengan ringkasan hash SHA-256.
      </p>
    </div>

    <!-- Search Box -->
    <VerifySearchBox :initialValue="certDetails.uuid" :loading="isChecking" @verify="handleLookup" />

    <!-- Details Card when Valid -->
    <CertificateDetailsCard v-if="certDetails.uuid && isValid" :details="certDetails" @reset="resetVerification" @copyLink="copyValidationLink" />

    <!-- Not Found Card when Invalid -->
    <div v-else-if="certDetails.uuid && !isValid" class="bg-white rounded-2xl sm:rounded-3xl p-6 sm:p-8 border border-rose-200 shadow-[0_4px_20px_rgba(138,152,184,0.06)] space-y-4">
      <div class="flex items-center gap-3">
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">Tidak Terdaftar</span>
        <h2 class="text-base sm:text-lg font-bold text-[#0B0F19]">Sertifikat Tidak Ditemukan</h2>
      </div>
      <p class="text-xs sm:text-sm text-[#5B6475]">
        Kode <code class="font-mono text-rose-700 bg-rose-50 px-2 py-0.5 rounded">{{ certDetails.uuid }}</code> tidak ditemukan atau telah kedaluwarsa. Pastikan format kode adalah 36-karakter UUID yang sah dari lembar sertifikat resmi VeriText AI.
      </p>
      <button
        type="button"
        @click="resetVerification"
        class="px-5 py-2.5 rounded-full bg-[#0B0F19] text-white text-xs font-semibold hover:bg-slate-800 active:scale-[0.98] transition-colors transition-transform duration-150 shadow-xs cursor-pointer"
      >
        Periksa Kode Lain
      </button>
    </div>

    <!-- How It Works & Honest Claims (Default) -->
    <VerifyHowItWorks v-else />
  </div>
</template>
