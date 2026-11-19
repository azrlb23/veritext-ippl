<script setup lang="ts">
import { computed } from "vue";
import { VT_ICON_PATHS, type VtIconName } from "./vtIconPaths";

const props = withDefaults(
  defineProps<{
    name: VtIconName;
    tone?: "violet" | "current";
  }>(),
  { tone: "violet" },
);

const icon = computed(() => VT_ICON_PATHS[props.name]);
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      :d="icon.back"
      :fill="tone === 'current' ? 'currentColor' : '#8A3FE0'"
      :fill-opacity="tone === 'current' ? 0.28 : 0.22"
    />
    <path
      :d="icon.front"
      fill="currentColor"
      :fill-rule="icon.fillRule || 'nonzero'"
    />
  </svg>
</template>
