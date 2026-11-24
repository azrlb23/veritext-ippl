<script setup lang="ts">
import { computed, ref } from "vue";

const props = withDefaults(
  defineProps<{
    id: string;
    label: string;
    modelValue: string;
    type?: string;
    placeholder?: string;
    autocomplete?: string;
    disabled?: boolean;
    invalid?: boolean;
    revealable?: boolean;
    required?: boolean;
  }>(),
  { type: "text", placeholder: "", autocomplete: "off", disabled: false, invalid: false, revealable: false, required: true }
);
const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();

const input = ref<HTMLInputElement | null>(null);
const focused = ref(false);
const revealed = ref(false);
const inputType = computed(() => (props.revealable && revealed.value ? "text" : props.type));
const lineActive = computed(() => focused.value || props.invalid || props.modelValue.length > 0);
</script>

<template>
  <div class="relative w-full cursor-text" @click="input?.focus()">
    <div class="flex items-center justify-between">
      <label
        :for="id"
        class="select-none text-[13px] font-medium transition-colors duration-200"
        :class="invalid ? 'text-[#B91C1C]' : focused ? 'text-[#0F766E]' : 'text-[#5E5A6B]'"
      >{{ label }}</label>
      <button
        v-if="revealable"
        type="button"
        class="-my-3.5 -mr-1.5 inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-[#5E5A6B] transition-colors hover:bg-[#14111C]/[0.05] hover:text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
        :aria-label="revealed ? 'Sembunyikan kata sandi' : 'Lihat kata sandi'"
        :title="revealed ? 'Sembunyikan kata sandi' : 'Lihat kata sandi'"
        @click.stop="revealed = !revealed"
      >
        <svg v-if="revealed" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.584 10.587a2 2 0 0 0 2.828 2.826M9.363 5.365A9.466 9.466 0 0 1 12 5c4.478 0 8.268 2.943 9.543 7a9.97 9.97 0 0 1-1.563 3.029m-2.14 2.14A9.45 9.45 0 0 1 12 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 0 1 2.573-4.16" />
        </svg>
        <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7Z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
      </button>
    </div>

    <input
      :id="id"
      ref="input"
      :value="modelValue"
      :type="inputType"
      :required="required"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :disabled="disabled"
      class="block w-full bg-transparent pb-3 pt-2 text-[16px] font-medium text-[#14111C] placeholder:text-[#6B6679] focus:outline-none disabled:opacity-60"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @focus="focused = true"
      @blur="focused = false"
    />

    <div class="h-[2px] w-full rounded-full bg-[#14111C]/45"></div>
    <div
      class="absolute bottom-0 left-0 h-[3px] rounded-full transition-[width] duration-300 ease-out motion-reduce:transition-none"
      :class="[invalid ? 'bg-[#B91C1C]' : 'bg-[#0F766E]', lineActive ? 'w-full' : 'w-0']"
    ></div>
  </div>
</template>
