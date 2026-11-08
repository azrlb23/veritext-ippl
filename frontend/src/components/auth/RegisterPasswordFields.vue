<script setup lang="ts">
import { ref, computed } from "vue";

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

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const focusedField = ref<string | null>(null);

const passwordStrength = computed(() => {
  const p = props.password;
  if (!p) return { score: 0, label: "Kosong", color: "bg-transparent", textColor: "text-[#5B6475]" };
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
  <div class="space-y-2">
    <!-- Kata Sandi & Konfirmasi Sandi (Side-by-side) -->
    <div class="w-full flex items-center gap-2.5">
      <!-- Sandi -->
      <div class="flex-1 h-[52px] rounded-[14px] bg-[#F3F6FC] px-3.5 pt-1.5 pb-1 flex flex-col justify-between relative transition-all">
        <div class="flex items-center justify-between">
          <label for="reg-password" class="text-[11px] font-medium select-none" :class="focusedField === 'password' ? 'text-[#1560BD]' : 'text-[#5B6475]'">
            Kata sandi
          </label>
          <button type="button" @click="showPassword = !showPassword" class="text-[11px] text-[#5B6475] hover:text-[#0B0F19]">
            {{ showPassword ? 'Tutup' : 'Lihat' }}
          </button>
        </div>
        <input
          id="reg-password"
          :value="password"
          @input="emit('update:password', ($event.target as HTMLInputElement).value)"
          :type="showPassword ? 'text' : 'password'"
          required
          autocomplete="new-password"
          placeholder="Min. 8 karakter"
          :disabled="disabled"
          @focus="focusedField = 'password'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[14px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="focusedField === 'password' || password" class="absolute bottom-1 left-3.5 right-3.5 h-[2px] rounded-full bg-[#1A73D9]"></div>
      </div>

      <!-- Konfirmasi Sandi -->
      <div class="flex-1 h-[52px] rounded-[14px] bg-[#F3F6FC] px-3.5 pt-1.5 pb-1 flex flex-col justify-between relative transition-all">
        <div class="flex items-center justify-between">
          <label for="reg-confirm" class="text-[11px] font-medium select-none" :class="isPasswordMismatch ? 'text-[#B91C1C]' : (focusedField === 'confirm' ? 'text-[#1560BD]' : 'text-[#5B6475]')">
            Konfirmasi sandi
          </label>
          <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="text-[11px] text-[#5B6475] hover:text-[#0B0F19]">
            {{ showConfirmPassword ? 'Tutup' : 'Lihat' }}
          </button>
        </div>
        <input
          id="reg-confirm"
          :value="confirmPassword"
          @input="emit('update:confirmPassword', ($event.target as HTMLInputElement).value)"
          :type="showConfirmPassword ? 'text' : 'password'"
          required
          autocomplete="new-password"
          placeholder="Ulangi sandi"
          :disabled="disabled"
          @focus="focusedField = 'confirm'"
          @blur="focusedField = null"
          class="w-full bg-transparent text-[14px] font-medium text-[#0B0F19] placeholder:text-[#636B7A] focus:outline-none -mt-0.5"
        />
        <div v-if="isPasswordMismatch" class="absolute bottom-1 left-3.5 right-3.5 h-[2px] rounded-full bg-[#B91C1C]"></div>
        <div v-else-if="focusedField === 'confirm' || confirmPassword" class="absolute bottom-1 left-3.5 right-3.5 h-[2px] rounded-full bg-[#1A73D9]"></div>
      </div>
    </div>

    <!-- Password Strength Meter -->
    <div v-if="password.length > 0" class="w-full space-y-1 pt-0.5">
      <div class="flex items-center justify-between text-[11px]">
        <span class="text-[#5B6475]">Kekuatan kata sandi:</span>
        <span :class="['font-semibold', passwordStrength.textColor]">{{ passwordStrength.label }}</span>
      </div>
      <div class="grid grid-cols-3 gap-1.5 h-1 w-full bg-[#DCE3F0] rounded-full overflow-hidden">
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 1 ? passwordStrength.color : 'bg-transparent']"></div>
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 2 ? passwordStrength.color : 'bg-transparent']"></div>
        <div :class="['rounded-full transition-all duration-300', passwordStrength.score >= 3 ? passwordStrength.color : 'bg-transparent']"></div>
      </div>
    </div>
  </div>
</template>
