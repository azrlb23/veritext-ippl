<script setup lang="ts">
import { onMounted } from "vue";
import ProfileCard from "../components/akun/ProfileCard.vue";
import PasswordCard from "../components/akun/PasswordCard.vue";
import PlanStatusCard from "../components/akun/PlanStatusCard.vue";
import DeleteAccountCard from "../components/akun/DeleteAccountCard.vue";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
onMounted(() => { void authStore.fetchProfile(); });
</script>

<template>
  <div class="mx-auto max-w-[1360px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7">
    <div class="mb-6 max-w-4xl">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Data Anda, Anda yang atur.
      </h1>
    </div>
    <div class="grid gap-6 lg:grid-cols-2 lg:items-stretch">
      <ProfileCard />
      <PasswordCard />
    </div>
    <div v-if="!authStore.isAdmin" class="mt-6"><PlanStatusCard /></div>
    <div class="mt-6"><DeleteAccountCard /></div>
  </div>
</template>
