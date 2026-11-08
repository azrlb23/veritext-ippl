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

export const chatService = {
  async paraphrase(sentenceId: string, mode: "SENTENCE" | "PARAGRAPH" | "FULL_PAGE" = "SENTENCE") {
    const res = await apiClient.post<{ data: ParaphraseResponseData }>("/chat/paraphrase", {
      sentence_id: sentenceId,
      mode,
    });
    return res.data.data;
  },

  async applyParaphrase(sentenceId: string, selectedText: string) {
    const res = await apiClient.post<{ data: ApplyParaphraseResponseData }>("/chat/apply-paraphrase", {
      sentence_id: sentenceId,
      selected_text: selectedText,
    });
    return res.data.data;
  },

  async sendMessage(documentId: string, prompt: string, sentenceId?: string) {
    const res = await apiClient.post<{ data: ChatMessageResponseData }>("/chat/message", {
      document_id: documentId,
      prompt,
      sentence_id: sentenceId || undefined,
    });
    return res.data.data;
  },
};
