<script setup lang="ts">
import { VtIcon } from "../common";
import { formatDate, isActiveStatus, isFailedStatus, stageLabel, type AuditTaskRow } from "../../composables/useAuditTasks";

withDefaults(defineProps<{ task: AuditTaskRow; allowDelete?: boolean }>(), { allowDelete: true });
defineEmits<{ (e: "open", id: string): void; (e: "cancel", id: string): void; (e: "delete", documentId: string): void }>();

const scoreTone = (s: number) => (s <= 20 ? "text-[#047857]" : s <= 40 ? "text-[#B45309]" : "text-[#B91C1C]");
</script>

<template>
  <li class="-mx-2 flex flex-col gap-4 rounded-[16px] px-2 py-5 transition-colors hover:bg-[#F3EEFA]/45 sm:flex-row sm:items-center sm:gap-6">
    <div class="flex min-w-0 flex-1 items-center gap-3.5">
      <VtIcon name="document" class="hidden h-5 w-5 shrink-0 text-[#14111C] sm:block" />
      <div class="min-w-0 flex-1">
        <p class="truncate text-[16px] font-semibold tracking-[-0.01em] text-[#14111C]">{{ task.title }}</p>
        <p class="mt-1 text-[14px] text-[#5E5A6B]">
          {{ formatDate(task.createdAt) }} - {{ task.depth === "FULL" ? "Audit penuh" : "Pindai cepat" }}
        </p>
      </div>
    </div>

    <div class="flex items-center justify-between gap-4 sm:justify-end sm:gap-6">
      <div class="min-w-[104px] sm:text-right">
        <template v-if="isActiveStatus(task.status)">
          <p class="text-[15px] font-semibold tabular-nums text-[#6D28D9]">Diproses {{ task.progress }}%</p>
          <p class="text-[13px] text-[#5E5A6B]">{{ stageLabel(task.stage) }}</p>
        </template>
        <p v-else-if="isFailedStatus(task.status)" class="text-[15px] font-medium text-[#B91C1C]">
          {{ task.status === "CANCELLED" ? "Dibatalkan" : "Gagal" }}
        </p>
        <template v-else>
          <p class="text-[32px] font-semibold leading-none tabular-nums tracking-[-0.04em]" :class="task.score !== null ? scoreTone(task.score) : 'text-[#5E5A6B]'">
            {{ task.score !== null ? task.score.toFixed(1).replace(".", ",") + "%" : "-" }}
          </p>
          <p class="mt-1 text-[13px] text-[#5E5A6B]">kemiripan</p>
        </template>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          v-if="isActiveStatus(task.status)"
          type="button"
          class="inline-flex h-11 cursor-pointer items-center rounded-full px-5 text-[14px] font-semibold text-[#B91C1C] transition-colors hover:bg-[#FEE2E2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          @click="$emit('cancel', task.id)"
        >Batalkan</button>
        <button
          v-else-if="task.status === 'SUCCESS'"
          type="button"
          class="inline-flex h-11 cursor-pointer items-center rounded-full bg-[#F3EEFA] px-5 text-[14px] font-semibold text-[#14111C] transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          @click="$emit('open', task.id)"
        >Buka laporan</button>
        <button
          v-if="allowDelete !== false && task.documentId && !isActiveStatus(task.status)"
          type="button"
          class="inline-flex h-11 cursor-pointer items-center rounded-full px-4 text-[14px] font-semibold text-[#B91C1C] transition-colors hover:bg-[#FEE2E2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8A3FE0]"
          @click="$emit('delete', task.documentId)"
        >Hapus</button>
      </div>
    </div>
  </li>
</template>
