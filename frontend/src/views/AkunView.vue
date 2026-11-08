<script setup lang="ts">
import ProfileCard from "../components/akun/ProfileCard.vue";
import PasswordCard from "../components/akun/PasswordCard.vue";
import DeleteAccountCard from "../components/akun/DeleteAccountCard.vue";
</script>

<template>
  <div class="mx-auto max-w-[1040px] px-4 pb-24 pt-8 font-sans sm:px-6 sm:pt-12">
    <div class="mb-9 max-w-2xl">
      <p class="text-[14px] font-medium text-[#5E5A6B]">Akun</p>
      <h1 class="mt-3 text-[36px] font-semibold leading-[1.08] tracking-[-0.045em] text-[#14111C] sm:text-[52px]">
        Data Anda, <span class="vt-accent">Anda yang atur.</span>
      </h1>
    </div>
    <div class="grid gap-6 lg:grid-cols-2 lg:items-start">
      <ProfileCard />
      <PasswordCard />
    </div>
    <div class="mt-6"><DeleteAccountCard /></div>
  </div>
</template>
