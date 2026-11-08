<script setup lang="ts">
import { computed } from "vue";
import AuthField from "./AuthField.vue";

interface Props {
  password: string;
  confirmPassword: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

const emit = defineEmits<{
  (e: "update:password", val: string): void;
  (e: "update:confirmPassword", val: string): void;
}>();

const passwordStrength = computed(() => {
  const p = props.password;
  if (!p) return { score: 0, label: "Kosong", color: "bg-transparent", textColor: "text-[#5E5A6B]" };
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++;
  if (/[0-9]/.test(p) || /[^A-Za-z0-9]/.test(p)) score++;

  if (score === 1) return { score: 1, label: "Lemah", color: "bg-[#B91C1C]", textColor: "text-[#B91C1C]" };
  if (score === 2) return { score: 2, label: "Sedang", color: "bg-[#C2410C]", textColor: "text-[#C2410C]" };
  return { score: 3, label: "Kuat", color: "bg-[#15803D]", textColor: "text-[#15803D]" };
});

const isPasswordMismatch = computed(() => {
  return props.confirmPassword.length > 0 && props.password !== props.confirmPassword;
});

</script>

<template>
  <div class="space-y-4">
    <div class="grid w-full gap-6 sm:grid-cols-2 sm:gap-5">
      <AuthField
        id="reg-password"
        label="Kata sandi"
        type="password"
        revealable
        autocomplete="new-password"
        placeholder="Min. 8 karakter"
        :model-value="password"
        :disabled="disabled"
        @update:model-value="emit('update:password', $event)"
      />
      <AuthField
        id="reg-confirm"
        label="Konfirmasi sandi"
        type="password"
        revealable
        autocomplete="new-password"
        placeholder="Ulangi sandi"
        :model-value="confirmPassword"
        :disabled="disabled"
        :invalid="isPasswordMismatch"
        @update:model-value="emit('update:confirmPassword', $event)"
      />
    </div>

    <div v-if="password.length > 0" class="w-full space-y-1.5">
      <div class="flex items-center justify-between text-[12.5px]">
        <span class="text-[#5E5A6B]">Kekuatan kata sandi</span>
        <span :class="['font-semibold', passwordStrength.textColor]">{{ passwordStrength.label }}</span>
      </div>
      <div class="grid h-1.5 w-full grid-cols-3 gap-1.5 overflow-hidden rounded-full bg-[#E6E0EF]">
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 1 ? passwordStrength.color : 'bg-transparent']"></div>
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 2 ? passwordStrength.color : 'bg-transparent']"></div>
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 3 ? passwordStrength.color : 'bg-transparent']"></div>
      </div>
    </div>
  </div>
</template>
