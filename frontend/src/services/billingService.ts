import { apiClient } from "./api";
import type { TokenWallet, Invoice } from "../types";

export interface TopupResult {
  order_id: string;
  snap_token: string;
  payment_ready: boolean;
  client_key?: string | null;
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
};
