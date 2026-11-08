<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

interface LinkItem { name: string; to: string }
const props = defineProps<{ links: LinkItem[]; isActive: (to: string) => boolean }>();

const items = ref<HTMLElement[]>([]);
const hovered = ref<number | null>(null);
const activeIndex = computed(() => props.links.findIndex((l) => props.isActive(l.to)));
const target = computed(() => (hovered.value !== null ? hovered.value : activeIndex.value));
const indicator = ref({ transform: "translateX(0px)", width: "0px", opacity: 0 });

function setItem(el: unknown, i: number) {
  if (el) items.value[i] = el as HTMLElement;
}

function measure() {
  const el = items.value[target.value];
  if (!el) {
    indicator.value = { ...indicator.value, opacity: 0 };
    return;
  }
  indicator.value = { transform: `translateX(${el.offsetLeft}px)`, width: `${el.offsetWidth}px`, opacity: 1 };
}

watch([target, () => props.links], () => nextTick(measure));
onMounted(() => {
  measure();
  window.addEventListener("resize", measure);
  document.fonts?.ready.then(measure);
});
onBeforeUnmount(() => window.removeEventListener("resize", measure));
</script>

<template>
  <nav class="relative items-center rounded-full bg-[#14111C]/[0.05] p-1" aria-label="Navigasi utama" @mouseleave="hovered = null">
    <span
      class="absolute bottom-1 left-0 top-1 rounded-full bg-white shadow-lift transition-[transform,width,opacity] duration-300 ease-out motion-reduce:transition-none"
      :style="indicator"
      aria-hidden="true"
    ></span>
    <router-link
      v-for="(item, i) in links"
      :key="item.to"
      :ref="(el) => setItem((el as any)?.$el ?? el, i)"
      :to="item.to"
      :aria-current="isActive(item.to) ? 'page' : undefined"
      class="relative z-10 inline-flex h-10 cursor-pointer items-center whitespace-nowrap rounded-full px-3.5 text-[13.5px] font-medium transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0] xl:px-5 xl:text-[14.5px]"
      :class="isActive(item.to) || hovered === i ? 'text-[#14111C]' : 'text-[#5E5A6B]'"
      @mouseenter="hovered = i"
      @focus="hovered = i"
      @blur="hovered = null"
    >
      {{ item.name }}
    </router-link>
  </nav>
</template>
