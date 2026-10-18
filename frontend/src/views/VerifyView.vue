<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  VerificationBadge,
  CertificateDetailsCard,
  CertificateLookup,
  type CertificateDetails,
} from "../components/verify";
import { useNotification } from "../composables";

const route = useRoute();
const router = useRouter();
const { showNotification } = useNotification();

const uuidParam = (route.params.uuid as string) || "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const isValid = ref(uuidParam !== "invalid");
const isChecking = ref(false);

const certDetails = ref<CertificateDetails>({
  uuid: uuidParam,
  title: "Pengaruh Algoritma Rekomendasi Terhadap Polaritas Opini Publik.pdf",
  examiner: "Dr. Budi Santoso",
  institution: "Universitas Indonesia",
  auditDate: "11 Oktober 2026, 20:30 WIB",
  compositeScore: 14.8,
  lexicalScore: 14.5,
  semanticScore: 18.2,
  styloScore: 8.0,
});

function handleLookup(uuid: string) {
  isChecking.value = true;
  setTimeout(() => {
    isChecking.value = false;
    const valid = !uuid.toLowerCase().includes("invalid");
    isValid.value = valid;
    certDetails.value.uuid = uuid;
    if (valid) {
      showNotification(`Sertifikat ${uuid.slice(0, 8)}... berhasil divalidasi.`, "success", "Validasi Berhasil");
    } else {
      showNotification("Kode sertifikat tidak ditemukan atau tidak valid.", "error", "Validasi Gagal");
    }
    router.replace(`/verify/${uuid}`);
  }, 400);
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 py-12 space-y-8">
    <!-- Certificate Lookup Input Bar -->
    <CertificateLookup
      :initialValue="certDetails.uuid"
      :loading="isChecking"
      @verify="handleLookup"
    />

    <!-- Verification Status Banner -->
    <VerificationBadge
      :isValid="isValid"
      :uuid="certDetails.uuid"
    />

    <!-- Summary Details Card with Gauge -->
    <CertificateDetailsCard v-if="isValid" :details="certDetails" />

    <div class="text-center text-xs text-audyr-ash">
      Halaman ini bersifat terbuka dan dapat diakses siapa saja untuk membuktikan keaslian laporan tanpa memerlukan autentikasi login.
    </div>
  </div>
</template>
