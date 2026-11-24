import { apiClient } from "./api";
import type { AuditTask, AuditReport } from "../types";

const MIME_TYPES: Record<"docx" | "pdf", string> = {
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  pdf: "application/pdf",
};

function sanitizeTitle(documentTitle: string): string {
  return (
    documentTitle
      .replace(/\.(pdf|docx?|txt)$/i, "")
      .trim()
      .replace(/[^a-zA-Z0-9_\-]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_+|_+$/g, "") || "Naskah"
  );
}

function triggerBlobDownload(data: BlobPart, mimeType: string, filename: string) {
  const blob = new Blob([data], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

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
    const res = await apiClient.get<{ data: { items: AuditTask[]; total: number; page?: number; pages?: number } }>("/audits/tasks", {
      params: { page, limit, search },
    });
    return res.data.data;
  },

  async exportHistoryCsv() {
    const res = await apiClient.get("/audits/history/export-csv", { responseType: "blob" });
    triggerBlobDownload(res.data, "text/csv;charset=utf-8;", "veritext_audit_history.csv");
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

  async downloadPdfReport(reportId: string, documentTitle: string = "Naskah") {
    const res = await apiClient.get(`/reports/${reportId}/export-pdf`, {
      responseType: "blob",
    });
    const filename = `Sertifikat_VeriText_${sanitizeTitle(documentTitle)}.pdf`;
    triggerBlobDownload(res.data, "application/pdf", filename);
    return filename;
  },

  async fetchAnnotatedPdfPreviewUrl(reportId: string): Promise<string> {
    const res = await apiClient.get(`/reports/${reportId}/preview-pdf`, {
      responseType: "blob",
    });
    return window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
  },

  async downloadRevisedDocument(reportId: string, format: "docx" | "pdf", documentTitle: string = "Naskah") {
    const res = await apiClient.get(`/reports/${reportId}/export-document`, {
      params: { format },
      responseType: "blob",
    });
    const filename = `Revisi_VeriText_${sanitizeTitle(documentTitle)}.${format}`;
    triggerBlobDownload(res.data, MIME_TYPES[format], filename);
    return filename;
  },
};
