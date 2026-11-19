import { apiClient } from "./api";
import type { TokenWallet, Invoice } from "../types";

export interface TopupResult {
  order_id: string;
  snap_token: string;
  payment_ready: boolean;
  client_key?: string | null;
  is_production?: boolean;
}

export const billingService = {
  async getWallet() {
    const res = await apiClient.get<{ data: TokenWallet }>("/billing/wallet");
    return res.data.data;
  },

  async topup(packageId: string, tokenAmount?: number) {
    const res = await apiClient.post<{ data: TopupResult }>("/billing/topup", {
      package_id: packageId,
      token_amount: tokenAmount,
    });
    return res.data.data;
  },

  async listInvoices() {
    const res = await apiClient.get<{ data: Invoice[] }>("/billing/invoices");
    return res.data.data;
  },

  async downloadInvoicePdf(orderId: string) {
    const res = await apiClient.get(`/billing/invoices/${encodeURIComponent(orderId)}/pdf`, {
      responseType: "blob",
    });
    const safeOrder = orderId.replace(/[^a-zA-Z0-9_\-]/g, "_") || "transaksi";
    const filename = `Kuitansi_VeriText_${safeOrder}.pdf`;
    const blob = new Blob([res.data], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return filename;
  },
};
