import { apiClient } from "./api";
import type { TokenWallet, Invoice } from "../types";

export const billingService = {
  async getWallet() {
    const res = await apiClient.get<{ data: TokenWallet }>("/billing/wallet");
    return res.data.data;
  },

  async topup(packageId: string) {
    const res = await apiClient.post<{ data: { order_id: string; snap_token: string } }>("/billing/topup", {
      package_id: packageId,
    });
    return res.data.data;
  },

  async listInvoices() {
    const res = await apiClient.get<{ data: Invoice[] }>("/billing/invoices");
    return res.data.data;
  },
};
