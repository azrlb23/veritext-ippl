export type InvoiceStatus = "PENDING" | "PAID" | "EXPIRED" | "FAILED" | "CANCEL";

export interface TokenWallet {
  id: string;
  balance: number;
  updated_at: string;
}

export interface TokenTransaction {
  id: string;
  transaction_type: string;
  amount: number;
  balance_after: number;
  reference_id?: string | null;
  note?: string | null;
  created_at: string;
}

export interface Invoice {
  id: string;
  order_id: string;
  package_name: string;
  token_amount: number;
  gross_amount: number;
  payment_method?: string | null;
  status: InvoiceStatus;
  paid_at?: string | null;
  expires_at: string;
  created_at: string;
}
