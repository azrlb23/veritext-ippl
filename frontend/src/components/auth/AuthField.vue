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
        :class="invalid ? 'text-[#B91C1C]' : focused ? 'text-[#6D28D9]' : 'text-[#5E5A6B]'"
      >{{ label }}</label>
      <button
        v-if="revealable"
        type="button"
        class="-my-3.5 -mr-2 cursor-pointer px-2 py-3.5 text-[13px] font-medium text-[#5E5A6B] transition-colors hover:text-[#14111C]"
        @click.stop="revealed = !revealed"
      >{{ revealed ? "Sembunyikan" : "Lihat" }}</button>
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
      :class="[invalid ? 'bg-[#B91C1C]' : 'bg-[#8A3FE0]', lineActive ? 'w-full' : 'w-0']"
    ></div>
  </div>
</template>
