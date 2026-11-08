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
      examiner: res?.examiner_name || "Pengguna terdaftar",
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

async function shareValidationLink() {
  const url = window.location.href;
  if (navigator.share) {
    try {
      await navigator.share({ title: "Sertifikat VeriText AI", url });
      return;
    } catch (err) {
      if ((err as DOMException).name === "AbortError") return;
    }
  }
  await navigator.clipboard?.writeText(url);
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
  <div class="mx-auto max-w-[1180px] px-4 pb-16 pt-8 font-sans sm:px-6 sm:pt-14">
    <div class="mx-auto mb-10 max-w-2xl text-center animate-fade-up">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Verifikasi sertifikat</p>
      <h1 class="mt-3 text-[38px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[56px]">
        Pastikan sertifikat itu <span class="vt-accent">benar-benar asli.</span>
      </h1>
      <p class="mx-auto mt-5 max-w-[520px] text-[16px] leading-[1.65] text-[#4B4757] sm:text-[17px]">
        Masukkan kode UUID dari lembar sertifikat atau pindai kode QR-nya. Hasilnya langsung tampil di sini.
      </p>
    </div>

    <div class="animate-fade-up [animation-delay:150ms]">
      <VerifySearchBox :initialValue="certDetails.uuid" :loading="isChecking" @verify="handleLookup" />
    </div>

    <div class="mt-14 animate-fade-up [animation-delay:300ms]">
      <div v-if="isChecking" class="mx-auto flex max-w-[620px] items-center gap-5 rounded-[36px] bg-white p-7 shadow-float sm:p-9" role="status">
        <svg class="h-9 w-9 shrink-0 animate-spin motion-reduce:animate-none" viewBox="0 0 36 36" fill="none" aria-hidden="true">
          <circle cx="18" cy="18" r="15" stroke="#EFEAF6" stroke-width="4" />
          <path d="M18 3 a15 15 0 0 1 15 15" stroke="#8A3FE0" stroke-width="4" stroke-linecap="round" />
        </svg>
        <div>
          <div class="text-[17px] font-semibold tracking-[-0.02em] text-[#14111C]">Memeriksa sertifikat</div>
          <div class="mt-0.5 text-[13.5px] text-[#5E5A6B]">Mencocokkan kode dengan catatan audit resmi.</div>
        </div>
      </div>

      <CertificateDetailsCard v-else-if="certDetails.uuid && isValid" 
        :details="certDetails"
        @reset="resetVerification" @copyLink="shareValidationLink" />

      <div v-else-if="certDetails.uuid && !isValid" class="mx-auto max-w-[760px] rounded-[36px] bg-white p-8 shadow-float sm:p-10">
        <h2 class="text-[22px] font-semibold tracking-[-0.03em] text-[#14111C]">Sertifikat tidak ditemukan</h2>
        <p class="mt-3 text-[15px] leading-[1.7] text-[#4B4757]">
          Kode <code class="rounded-[8px] bg-[#FEE2E2] px-2 py-0.5 font-mono text-[13px] text-[#991B1B]">{{ certDetails.uuid }}</code>
          tidak terdaftar atau sudah kedaluwarsa. Pastikan kode terdiri dari 36 karakter dan disalin persis dari lembar sertifikat resmi VeriText AI.
        </p>
        <button
          type="button"
          @click="resetVerification"
          class="mt-7 inline-flex h-11 cursor-pointer items-center rounded-full bg-[#14111C] px-6 text-[13.5px] font-semibold text-white shadow-btn-dark transition-transform duration-200 hover:-translate-y-0.5"
        >
          Periksa kode lain
        </button>
      </div>

      <VerifyHowItWorks v-else />
    </div>
  </div>
</template>
