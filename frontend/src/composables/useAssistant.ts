import { computed, onMounted, ref } from "vue";
import { chatService, type ChatHistoryItem, type ChatSessionItem } from "../services/chatService";
import { documentService } from "../services/documentService";
import { useAuthStore } from "../stores/auth";
import type { DocumentItem } from "../types";

const GUARDRAIL = "Permintaan ini tidak bisa diproses karena di luar batas etika penulisan.";
const QUOTA = "Kuota coba gratis habis. Beli token atau upgrade ke Premium untuk melanjutkan.";

export function friendlyChatError(err: any): string {
  const detail: string = err?.response?.data?.detail || "";
  if (detail.includes("CHAT_001")) return GUARDRAIL;
  if (detail.includes("CHAT_002") || detail.includes("AUDIT_001")) return QUOTA;
  return detail || "Asisten belum bisa menjawab. Coba lagi sebentar lagi.";
}

export function useAssistant() {
  const authStore = useAuthStore();
  const sessions = ref<ChatSessionItem[]>([]);
  const documents = ref<DocumentItem[]>([]);
  const activeId = ref<string | null>(null);
  const messages = ref<ChatHistoryItem[]>([]);
  const selectedDocs = ref<string[]>([]);
  const sending = ref(false);
  const error = ref("");
  const trialLeft = ref<number | null>(null);

  const activeSession = computed(() => sessions.value.find((s) => s.id === activeId.value) || null);

  async function loadSessions() {
    sessions.value = await chatService.listSessions().catch(() => []);
  }

  async function openSession(id: string | null) {
    activeId.value = id;
    error.value = "";
    messages.value = id ? await chatService.getMessages(id).catch(() => []) : [];
  }

  async function send(prompt: string) {
    error.value = "";
    sending.value = true;
    const local: ChatHistoryItem = { id: `local-${Date.now()}`, role: "USER", content: prompt, created_at: new Date().toISOString() };
    messages.value.push(local);
    try {
      const res = await chatService.sendMessage(prompt, { documentIds: activeId.value ? [] : selectedDocs.value, sessionId: activeId.value || undefined });
      messages.value.push({ id: res.message_id, role: "ASSISTANT", content: res.content, created_at: new Date().toISOString() });
      activeId.value = res.session_id;
      trialLeft.value = res.ai_trial_remaining;
      await Promise.all([loadSessions(), authStore.fetchProfile()]);
    } catch (err: any) {
      messages.value = messages.value.filter((m) => m.id !== local.id);
      error.value = friendlyChatError(err);
    } finally {
      sending.value = false;
    }
  }

  async function removeSession(id: string) {
    await chatService.deleteSession(id);
    if (activeId.value === id) await openSession(null);
    await loadSessions();
  }

  onMounted(async () => {
    await loadSessions();
    documents.value = (await documentService.list(1, 50).catch(() => ({ items: [] as DocumentItem[] }))).items;
  });

  return { sessions, documents, activeId, activeSession, messages, selectedDocs, sending, error, trialLeft, openSession, send, removeSession };
}
