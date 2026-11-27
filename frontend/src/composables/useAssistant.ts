import { computed, onMounted, ref, watch } from "vue";
import { auditService } from "../services/auditService";
import { chatService, type ChatHistoryItem, type ChatSessionItem } from "../services/chatService";
import { documentService } from "../services/documentService";
import { useAuthStore } from "../stores/auth";
import type { AuditTask, DocumentItem } from "../types";

type AuditTaskWithReport = AuditTask & { report_id?: string | null };

const GUARDRAIL = "Permintaan ini tidak bisa diproses karena di luar batas etika penulisan.";
const QUOTA = "Kuota coba gratis habis. Beli token atau upgrade ke Premium untuk melanjutkan.";

export function friendlyChatError(err: any): string {
  const detail: string = err?.response?.data?.detail || "";
  if (detail.includes("CHAT_001")) return GUARDRAIL;
  if (detail.includes("CHAT_002") || detail.includes("AUDIT_001")) return QUOTA;
  return detail.replace(/^[A-Z0-9_]+:\s*/, "") || "Asisten belum bisa menjawab. Coba lagi sebentar lagi.";
}

const NEW_KEY = "__new__";
const keyOf = (id: string | null) => id || NEW_KEY;

export function useAssistant() {
  const authStore = useAuthStore();
  const sessions = ref<ChatSessionItem[]>([]);
  const documents = ref<DocumentItem[]>([]);
  const auditTasks = ref<AuditTaskWithReport[]>([]);
  const reportIdsByTask = ref<Record<string, string>>({});
  const activeId = ref<string | null>(null);
  const messagesBySession = ref<Record<string, ChatHistoryItem[]>>({});
  const sendingBySession = ref<Record<string, boolean>>({});
  const errorBySession = ref<Record<string, string>>({});
  const drafts = ref<Record<string, string>>({});
  const selectedDocs = ref<string[]>([]);
  const trialLeft = ref<number | null>(null);
  const preferredEngine = ref<"auto" | "ollama" | "gemini">("auto");
  const taskMode = ref<"QA_DOCUMENT" | "PARAPHRASE_TASK" | "STYLE_REVIEW">("QA_DOCUMENT");
  const lastEngine = ref("");

  const messages = computed(() => messagesBySession.value[keyOf(activeId.value)] || []);
  const sending = computed(() => Boolean(sendingBySession.value[keyOf(activeId.value)]));
  const error = computed({
    get: () => errorBySession.value[keyOf(activeId.value)] || "",
    set: (val: string) => { errorBySession.value = { ...errorBySession.value, [keyOf(activeId.value)]: val }; },
  });
  const draft = computed({
    get: () => drafts.value[keyOf(activeId.value)] || "",
    set: (val: string) => { drafts.value = { ...drafts.value, [keyOf(activeId.value)]: val }; },
  });

  const activeSession = computed(() => sessions.value.find((s) => s.id === activeId.value) || null);
  const linkedAudit = computed(() => {
    const docId = activeSession.value?.document_ids?.[0] || selectedDocs.value[0];
    if (!docId) return null;
    const match = auditTasks.value.find((t) => t.document_id === docId && t.status === "SUCCESS");
    if (!match) return null;
    const taskId = match.task_id || match.id || "";
    const reportId = match.report_id || reportIdsByTask.value[taskId] || "";
    return { documentId: docId, reportId, taskId };
  });

  watch(linkedAudit, async (val) => {
    if (val?.taskId && !val.reportId) {
      const rep = await auditService.getReport(val.taskId).catch(() => null);
      if (rep?.id) reportIdsByTask.value = { ...reportIdsByTask.value, [val.taskId]: rep.id };
    }
  }, { immediate: true });

  async function loadSessions() {
    sessions.value = await chatService.listSessions().catch(() => []);
  }

  async function openSession(id: string | null) {
    activeId.value = id;
    if (id && !sendingBySession.value[id] && !messagesBySession.value[id]) {
      const msgs = await chatService.getMessages(id).catch(() => []);
      if (!sendingBySession.value[id]) {
        messagesBySession.value = { ...messagesBySession.value, [id]: msgs };
      }
    }
  }

  async function send(prompt: string) {
    const originId = activeId.value;
    const originKey = keyOf(originId);
    drafts.value = { ...drafts.value, [originKey]: "" };
    errorBySession.value = { ...errorBySession.value, [originKey]: "" };
    sendingBySession.value = { ...sendingBySession.value, [originKey]: true };
    const local: ChatHistoryItem = { id: `local-${Date.now()}`, role: "USER", content: prompt, created_at: new Date().toISOString() };
    messagesBySession.value = { ...messagesBySession.value, [originKey]: [...(messagesBySession.value[originKey] || []), local] };
    try {
      const res = await chatService.sendMessage(prompt, {
        documentIds: originId ? [] : selectedDocs.value,
        sessionId: originId || undefined,
        preferredEngine: preferredEngine.value,
        taskMode: taskMode.value,
      });
      const replyMsg: ChatHistoryItem = { id: res.message_id, role: "ASSISTANT", content: res.content, created_at: new Date().toISOString() };
      const nextMessages = { ...messagesBySession.value, [res.session_id]: [...(messagesBySession.value[originKey] || []), replyMsg] };
      if (originKey === NEW_KEY) nextMessages[NEW_KEY] = [];
      messagesBySession.value = nextMessages;
      if (activeId.value === originId) activeId.value = res.session_id;
      trialLeft.value = res.ai_trial_remaining;
      lastEngine.value = res.active_engine || "";
      await Promise.all([loadSessions(), authStore.fetchProfile()]);
    } catch (err: any) {
      messagesBySession.value = { ...messagesBySession.value, [originKey]: (messagesBySession.value[originKey] || []).filter((m) => m.id !== local.id) };
      errorBySession.value = { ...errorBySession.value, [originKey]: friendlyChatError(err) };
    } finally {
      sendingBySession.value = { ...sendingBySession.value, [originKey]: false };
    }
  }

  async function removeSession(id: string) {
    await chatService.deleteSession(id);
    if (activeId.value === id) await openSession(null);
    await loadSessions();
  }

  onMounted(async () => {
    const [, docsRes, historyRes] = await Promise.all([
      loadSessions(),
      documentService.list(1, 50).catch(() => ({ items: [] as DocumentItem[] })),
      auditService.getHistory(1, 50).catch(() => ({ items: [] as AuditTask[] })),
    ]);
    documents.value = docsRes.items;
    auditTasks.value = historyRes.items as AuditTaskWithReport[];
  });

  return {
    sessions, documents, activeId, activeSession, linkedAudit, messages, selectedDocs,
    sending, error, draft, trialLeft, preferredEngine, taskMode, lastEngine,
    openSession, send, removeSession,
  };
}
