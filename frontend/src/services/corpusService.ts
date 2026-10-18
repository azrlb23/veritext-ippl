import { apiClient } from "./api";
import type { CorpusDocument } from "../types";

export const corpusService = {
  async list(category?: string, page: number = 1, limit: number = 20) {
    const res = await apiClient.get<{ data: { items: CorpusDocument[]; total: number } }>("/corpus", {
      params: { category, page, limit },
    });
    return res.data.data;
  },

  async ingest(file: File, category?: string, academicYear?: string) {
    const formData = new FormData();
    formData.append("file", file);
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (academicYear) params.append("academic_year", academicYear);

    const res = await apiClient.post<{ data: { queued_count: number } }>(
      `/corpus/ingest?${params.toString()}`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return res.data.data;
  },

  async delete(id: string) {
    const res = await apiClient.delete(`/corpus/${id}`);
    return res.data;
  },
};
