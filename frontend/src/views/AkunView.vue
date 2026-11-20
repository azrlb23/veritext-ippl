<script setup lang="ts">
import ProfileCard from "../components/akun/ProfileCard.vue";
import PasswordCard from "../components/akun/PasswordCard.vue";
import DeleteAccountCard from "../components/akun/DeleteAccountCard.vue";
</script>

<template>
  <div class="mx-auto max-w-[1040px] px-4 pb-24 pt-5 font-sans sm:px-6 sm:pt-7">
    <div class="mb-6 max-w-4xl">
      <h1 class="text-[24px] font-semibold leading-[1.18] tracking-[-0.03em] text-[#14111C] sm:text-[28px]">
        Data Anda, Anda yang atur.
      </h1>
    </div>
    <div class="grid gap-6 lg:grid-cols-2 lg:items-start">
      <ProfileCard />
      <PasswordCard />
    </div>
    <div class="mt-6"><DeleteAccountCard /></div>
  </div>
</template>
