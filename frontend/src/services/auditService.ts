import { apiClient } from "./api";
import type { AuditTask, AuditReport } from "../types";

export const auditService = {
  async startAudit(documentId: string, depth: "TIER1_ONLY" | "FULL" = "FULL") {
    const res = await apiClient.post<{ data: AuditTask }>("/audits", {
      document_id: documentId,
      audit_depth: depth,
    });
    return res.data.data;
  },

  async getStatus(taskId: string) {
    const res = await apiClient.get<{ data: AuditTask }>(`/audits/${taskId}/status`);
    return res.data.data;
  },

  async cancelAudit(taskId: string) {
    const res = await apiClient.post(`/audits/${taskId}/cancel`);
    return res.data;
  },

  async getTasks(page: number = 1, limit: number = 20, search?: string) {
    const res = await apiClient.get<{ data: { items: AuditTask[]; total: number } }>("/audits/tasks", {
      params: { page, limit, search },
    });
    return res.data.data;
  },

  async getHistory(page: number = 1, limit: number = 20) {
    const res = await apiClient.get<{ data: { items: AuditTask[]; total: number } }>("/audits/history", {
      params: { page, limit },
    });
    return res.data.data;
  },

  async getReport(reportId: string) {
    const res = await apiClient.get<{ data: AuditReport }>(`/reports/${reportId}`);
    return res.data.data;
  },

  async verifyCertificate(verificationUuid: string) {
    const res = await apiClient.get<{ data: any }>(`/verify/${verificationUuid}`);
    return res.data.data;
  },
};
