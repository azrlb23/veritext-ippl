<script setup lang="ts">
type SkeletonShape = "text" | "circle" | "rectangle" | "table-row";

interface Props {
  shape?: SkeletonShape;
  count?: number;
  height?: string;
  width?: string;
}

withDefaults(defineProps<Props>(), {
  shape: "text",
  count: 1,
  height: "",
  width: "",
});
</script>

<template>
  <div class="space-y-2">
    <template v-if="shape === 'text'">
      <div
        v-for="i in count"
        :key="i"
        class="h-4 bg-[#ededed] rounded-[4px] animate-pulse"
        :style="{ width: width || (i === count && count > 1 ? '70%' : '100%'), height: height || undefined }"
      ></div>
    </template>

    <template v-else-if="shape === 'circle'">
      <div
        v-for="i in count"
        :key="i"
        class="rounded-full bg-[#ededed] animate-pulse inline-block"
        :style="{ width: width || '40px', height: height || '40px' }"
      ></div>
    </template>

    <template v-else-if="shape === 'rectangle'">
      <div
        v-for="i in count"
        :key="i"
        class="bg-[#ededed] rounded-[14px] animate-pulse"
        :style="{ width: width || '100%', height: height || '120px' }"
      ></div>
    </template>

    <template v-else-if="shape === 'table-row'">
      <div
        v-for="i in count"
        :key="i"
        class="flex items-center space-x-4 py-3 animate-pulse border-b border-[#ededed]"
      >
        <div class="h-4 bg-[#ededed] rounded-[4px] w-1/4"></div>
        <div class="h-4 bg-[#ededed] rounded-[4px] w-1/6"></div>
        <div class="h-4 bg-[#ededed] rounded-[4px] w-1/4"></div>
        <div class="h-4 bg-[#ededed] rounded-[4px] w-1/6"></div>
        <div class="h-4 bg-[#ededed] rounded-[4px] w-1/12 ml-auto"></div>
      </div>
    </template>
  </div>
</template>
