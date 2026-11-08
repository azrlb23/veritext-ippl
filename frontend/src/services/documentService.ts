import { apiClient } from "./api";
import type { DocumentItem, DocumentUploadResponse } from "../types";

export interface DocumentEstimate {
  word_count: number;
  token_cost: number;
  within_plan: boolean;
  max_free_words: number;
}

export const documentService = {
  async estimate(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post<{ data: DocumentEstimate }>("/documents/estimate", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data.data;
  },

  async upload(file: File, depth: "FULL" | "TIER1_ONLY" = "FULL") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("audit_depth", depth);
    const res = await apiClient.post<{ data: DocumentUploadResponse }>("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data.data;
  },

  async list(page: number = 1, limit: number = 20) {
    const res = await apiClient.get<{ data: { items: DocumentItem[]; total: number; page: number; limit: number } }>(
      "/documents",
      { params: { page, limit } }
    );
    return res.data.data;
  },

  async getById(id: string) {
    const res = await apiClient.get<{ data: DocumentItem }>(`/documents/${id}`);
    return res.data.data;
  },

  async delete(id: string) {
    const res = await apiClient.delete(`/documents/${id}`);
    return res.data;
  },
};
