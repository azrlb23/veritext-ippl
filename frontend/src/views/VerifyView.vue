<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  VerificationBadge,
  CertificateDetailsCard,
  CertificateLookup,
  type CertificateDetails,
} from "../components/verify";
import { useNotification } from "../composables";
import { auditService } from "../services/auditService";

const route = useRoute();
const router = useRouter();
const { showNotification } = useNotification();

const uuidParam = (route.params.uuid as string) || "";
const isValid = ref(false);
const isChecking = ref(false);

const certDetails = ref<CertificateDetails>({
  uuid: uuidParam,
  title: "",
  examiner: "",
  institution: "",
  auditDate: "",
  compositeScore: 0,
  lexicalScore: 0,
  semanticScore: 0,
  styloScore: 0,
});

async function handleLookup(targetUuid: string) {
  if (!targetUuid || !targetUuid.trim()) return;
  isChecking.value = true;
  try {
    const res = await auditService.verifyCertificate(targetUuid.trim());
    if (res && res.is_valid !== undefined) {
      isValid.value = res.is_valid;
      certDetails.value = {
        uuid: targetUuid,
        title: res.title || "",
        examiner: res.examiner_name || "",
        institution: res.institution || "",
        auditDate: res.audit_date || "",
        compositeScore: res.score_composite ?? 0,
        lexicalScore: res.score_lexical ?? 0,
        semanticScore: res.score_semantic ?? 0,
        styloScore: res.score_stylometric ?? 0,
      };
      if (res.is_valid) {
        showNotification(`Sertifikat ${targetUuid.slice(0, 8)}... berhasil divalidasi.`, "success", "Validasi Berhasil");
      } else {
        showNotification("Kode sertifikat tidak ditemukan atau tidak valid.", "error", "Validasi Gagal");
      }
      if (route.params.uuid !== targetUuid) {
        router.replace(`/verify/${targetUuid}`);
      }
    }
  } catch (err: any) {
    isValid.value = false;
    certDetails.value = {
      uuid: targetUuid,
      title: "",
      examiner: "",
      institution: "",
      auditDate: "",
      compositeScore: 0,
      lexicalScore: 0,
      semanticScore: 0,
      styloScore: 0,
    };
    showNotification(
      err?.response?.data?.detail || err?.message || "Kode sertifikat tidak ditemukan atau tidak valid.",
      "error",
      "Validasi Gagal"
    );
  } finally {
    isChecking.value = false;
  }
}

onMounted(() => {
  const currentParam = route.params.uuid as string | undefined;
  if (currentParam && currentParam.trim() && currentParam !== "invalid") {
    void handleLookup(currentParam.trim());
  }
});

watch(
  () => route.params.uuid,
  (newUuid) => {
    if (newUuid && typeof newUuid === "string" && newUuid !== certDetails.value.uuid) {
      void handleLookup(newUuid);
    }
  }
);
</script>

<template>
  <div class="relative max-w-3xl mx-auto px-4 sm:px-6 py-12 space-y-8">
    <!-- Ambient Warm Peach Radial Glow -->
    <div
      class="absolute top-0 left-1/2 -translate-x-1/2 -z-10 w-full max-w-4xl h-[420px] bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(251,225,209,0.5),rgba(255,255,255,0))] blur-3xl pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Editorial Header Section -->
    <div class="text-center space-y-3">
      <span class="inline-flex items-center px-3.5 py-1 rounded-full bg-[#fbe1d1] text-[#5d2a1a] text-xs font-semibold tracking-wide uppercase">
        Protokol Validasi Publik
      </span>
      <h1 class="font-serif text-3xl sm:text-4xl font-normal text-[#17191c] tracking-tight">
        Verifikasi Kriptografis Integritas Naskah
      </h1>
      <p class="text-xs sm:text-sm text-[#777b86] max-w-lg mx-auto leading-relaxed font-normal">
        Buktikan keaslian dokumen dan status sertifikasi audit akademik secara transparan tanpa memerlukan autentikasi akun.
      </p>
    </div>

    <!-- Certificate Lookup Input Bar -->
    <CertificateLookup
      :initialValue="certDetails.uuid"
      :loading="isChecking"
      @verify="handleLookup"
    />

    <!-- Verification Status Banner -->
    <VerificationBadge
      v-if="certDetails.uuid"
      :isValid="isValid"
      :uuid="certDetails.uuid"
    />

    <!-- Summary Details Card with Steep Donut Gauge -->
    <CertificateDetailsCard v-if="isValid && certDetails.title" :details="certDetails" />

    <div class="text-center text-xs text-[#777b86] font-normal">
      Halaman ini bersifat terbuka dan dapat diakses siapa saja untuk membuktikan keaslian laporan tanpa memerlukan autentikasi login.
    </div>
  </div>
</template>
