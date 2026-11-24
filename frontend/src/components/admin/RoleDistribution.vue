<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ distribution: Record<string, number>; loading?: boolean }>();

const ROLES = [
  { key: "FREE", label: "FREE", color: "#0F766E" },
  { key: "PREMIUM", label: "PREMIUM", color: "#D97706" },
  { key: "ADMIN", label: "ADMIN", color: "#4B4757" },
] as const;

const totalUsers = computed(() =>
  ROLES.reduce((sum, r) => sum + (props.distribution?.[r.key] || 0), 0)
);

const items = computed(() => {
  const total = totalUsers.value;
  return ROLES.map((r) => {
    const count = props.distribution?.[r.key] || 0;
    const pct = total > 0 ? (count / total) * 100 : 0;
    return {
      key: r.key,
      label: r.label,
      color: r.color,
      count,
      pct,
      pctText: `${pct.toFixed(1).replace(".", ",")}%`,
    };
  });
});
</script>

<template>
  <section class="rounded-[28px] border border-[#E8ECEB] bg-white p-6 sm:p-8" aria-labelledby="role-dist-title" :aria-busy="loading">
    <div class="flex items-baseline justify-between gap-4">
      <h2 id="role-dist-title" class="text-[20px] font-semibold tracking-[-0.03em] text-[#14111C]">Sebaran peran</h2>
      <p class="text-[14px] tabular-nums text-[#5E5A6B]">{{ loading ? "-" : `${totalUsers.toLocaleString("id-ID")} pengguna` }}</p>
    </div>

    <div class="mt-4 flex h-2 w-full overflow-hidden rounded-full bg-[#F1F5F4]" role="img" aria-label="Proporsi peran pengguna FREE, PREMIUM, dan ADMIN">
      <div
        v-for="item in items"
        :key="item.key"
        class="h-full transition-[width] duration-200"
        :style="{ width: `${item.pct}%`, backgroundColor: item.color }"
      />
    </div>

    <ul class="mt-6 space-y-4">
      <li v-for="item in items" :key="item.key">
        <div class="flex items-center justify-between gap-4 text-[14px]">
          <span class="inline-flex items-center gap-2 font-semibold text-[#14111C]">
            <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: item.color }" aria-hidden="true" />
            {{ item.label }}
          </span>
          <span class="tabular-nums text-[#4B4757]">
            <strong class="font-semibold text-[#14111C]">{{ loading ? "-" : item.count.toLocaleString("id-ID") }}</strong>
            <span class="ml-1.5 text-[#5E5A6B]">({{ loading ? "-" : item.pctText }})</span>
          </span>
        </div>
        <div class="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-[#F1F5F4]">
          <div
            class="h-full rounded-full transition-[width] duration-200"
            :style="{ width: `${item.pct}%`, backgroundColor: item.color }"
          />
        </div>
      </li>
    </ul>
  </section>
</template>
