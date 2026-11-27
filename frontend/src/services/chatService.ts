import { apiClient } from "./api";

export interface ParaphraseVariation {
  option_id: number;
  style: string;
  text: string;
  predicted_score: number;
}

export interface ParaphraseResponseData {
  sentence_id: string;
  mode: string;
  variations: ParaphraseVariation[];
  active_engine: string;
}

export interface ApplyParaphraseResponseData {
  sentence_id: string;
  current_text: string;
  match_type: string;
  new_similarity: number;
  new_composite_score: number;
  is_modified: boolean;
}

export interface ChatMessageResponseData {
  message_id: string;
  session_id: string;
  role: string;
  content: string;
  active_engine: string;
  ai_trial_remaining: number;
  balance: number;
  ai_chat_allowance_remaining: number;
}

export interface ChatSessionItem {
  id: string;
  title: string;
  document_ids: string[];
  last_message: string | null;
  message_count: number;
  updated_at: string;
}

export interface ChatHistoryItem {
  id: string;
  role: "USER" | "ASSISTANT";
  content: string;
  created_at: string;
}

export interface PrioritySentenceItem {
  sentence_id: string;
  text: string;
  match_type: string;
  similarity_score: number;
  source_title?: string | null;
}

export interface PrioritySentencesData { audit_task_id: string; report_id?: string | null; items: PrioritySentenceItem[]; }
export interface CheckSimilarityResult { lexical_overlap_pct: number; word_overlap_pct: number; is_improved: boolean; }

export const chatService = {
  async paraphrase(
    sentenceId: string,
    mode: "SENTENCE" | "PARAGRAPH" | "FULL_PAGE" = "SENTENCE",
    preferredEngine: string = "auto"
  ) {
    const res = await apiClient.post<{ data: ParaphraseResponseData }>("/chat/paraphrase", {
      sentence_id: sentenceId,
      mode,
      preferred_engine: preferredEngine,
    });
    return res.data.data;
  },

  async applyParaphrase(
    sentenceId: string,
    selectedText: string,
    mode: "SENTENCE" | "PARAGRAPH" | "FULL_PAGE" = "SENTENCE"
  ) {
    const res = await apiClient.post<{ data: ApplyParaphraseResponseData }>("/chat/apply-paraphrase", {
      sentence_id: sentenceId,
      selected_text: selectedText,
      mode,
    });
    return res.data.data;
  },

  async sendMessage(
    prompt: string,
    opts: { documentIds?: string[]; sessionId?: string; sentenceId?: string; preferredEngine?: string; taskMode?: string } = {}
  ) {
    const res = await apiClient.post<{ data: ChatMessageResponseData }>("/chat/message", {
      prompt,
      document_ids: opts.documentIds ?? [],
      session_id: opts.sessionId || undefined,
      sentence_id: opts.sentenceId || undefined,
      preferred_engine: opts.preferredEngine || "auto",
      task_mode: opts.taskMode || "QA_DOCUMENT",
    });
    return res.data.data;
  },

  async listSessions() {
    const res = await apiClient.get<{ data: ChatSessionItem[] }>("/chat/sessions");
    return res.data.data;
  },

  async getMessages(sessionId: string) {
    const res = await apiClient.get<{ data: ChatHistoryItem[] }>(`/chat/sessions/${sessionId}/messages`);
    return res.data.data;
  },

  async deleteSession(sessionId: string) {
    await apiClient.delete(`/chat/sessions/${sessionId}`);
  },

  async getPrioritySentences(documentId: string, limit: number = 5) {
    const res = await apiClient.get<{ data: PrioritySentencesData }>("/chat/priority-sentences", {
      params: { document_id: documentId, limit },
    });
    return res.data.data;
  },

  async checkSimilarity(originalText: string, rewrittenText: string) {
    const res = await apiClient.post<{ data: CheckSimilarityResult }>("/chat/check-similarity", {
      original_text: originalText,
      rewritten_text: rewrittenText,
    });
    return res.data.data;
  },
};
