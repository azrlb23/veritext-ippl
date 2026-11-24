<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import type { ChatSessionItem } from "../../services/chatService";

defineProps<{ sessions: ChatSessionItem[]; activeId: string | null }>();
const emit = defineEmits<{ (e: "open", id: string | null): void; (e: "remove", id: string): void }>();

const menuId = ref<string | null>(null);
const menuPos = ref({ x: 0, y: 0 });
const menuRef = ref<HTMLElement | null>(null);

function openContext(e: MouseEvent, id: string) {
  menuId.value = id;
  menuPos.value = { x: Math.min(e.clientX, window.innerWidth - 208), y: Math.min(e.clientY, window.innerHeight - 64) };
}
function confirmRemove() {
  if (!menuId.value) return;
  emit("remove", menuId.value);
  menuId.value = null;
}
function onDocClick(e: MouseEvent) {
  if (menuId.value && menuRef.value && !menuRef.value.contains(e.target as Node)) menuId.value = null;
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape" && menuId.value) menuId.value = null;
}
onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onKeydown);
});
onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div class="flex h-full flex-col">
    <button
      type="button"
      class="vt-btn-dark inline-flex h-12 w-full cursor-pointer items-center justify-center rounded-full px-6 text-[15px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2"
      @click="emit('open', null)"
    >Percakapan baru</button>

    <p v-if="sessions.length === 0" class="mt-6 px-1 text-[14px] leading-relaxed text-[#5E5A6B]">Percakapan Anda akan tersimpan di sini.</p>
    <ul v-else class="mt-4 flex-1 space-y-1 overflow-y-auto no-scrollbar">
      <li v-for="s in sessions" :key="s.id">
        <button
          type="button"
          title="Klik kanan untuk menghapus"
          class="block min-h-[56px] w-full cursor-pointer rounded-[20px] px-4 py-3 text-left transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          :class="activeId === s.id ? 'border border-[#D5ECE8] bg-[#EBF8F6] shadow-lift' : 'border border-transparent hover:bg-white/70'"
          @click="emit('open', s.id)"
          @contextmenu.prevent="openContext($event, s.id)"
        >
          <span class="block truncate text-[15px] font-semibold" :class="activeId === s.id ? 'text-[#0F766E]' : 'text-[#14111C]'">{{ s.title }}</span>
          <span class="mt-0.5 block truncate text-[13px] text-[#5E5A6B]">{{ s.last_message || "Belum ada pesan" }}</span>
        </button>
      </li>
    </ul>

    <Teleport to="body">
      <div
        v-if="menuId"
        ref="menuRef"
        role="menu"
        :style="{ left: `${menuPos.x}px`, top: `${menuPos.y}px` }"
        class="fixed z-[90] w-48 rounded-2xl border border-[#E8ECEB] bg-white p-1.5 shadow-float"
      >
        <button
          type="button"
          role="menuitem"
          class="flex h-11 w-full cursor-pointer items-center rounded-xl px-4 text-left text-[14px] font-medium text-[#B91C1C] transition-colors hover:bg-[#FEE2E2] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E]"
          @click="confirmRemove"
        >Hapus percakapan</button>
      </div>
    </Teleport>
  </div>
</template>
