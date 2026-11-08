import { onMounted, ref } from "vue";
import { billingService } from "../services/billingService";
import { useAuthStore } from "../stores/auth";
import { openSnap } from "../utils/midtransSnap";
import { useNotification } from "./useNotification";

export interface TokenPackage {
  id: string;
  name: string;
  tokens: number;
  price: number;
  note: string;
  featured?: boolean;
}

export interface PurchaseTarget {
  id: string;
  name: string;
  tokens: number;
  price: number;
  tokenAmount?: number;
}

export interface InvoiceRow {
  orderId: string;
  name: string;
  amount: number;
  status: string;
  date: string;
}

export const UNIT_PRICE = 2000;
export const UNIT_MIN = 5;
export const PACKAGES: TokenPackage[] = [
  { id: "pkg_starter", name: "Starter", tokens: 15, price: 25000, note: "Untuk satu sampai dua naskah pendek." },
  { id: "pkg_skripsi_pro", name: "Skripsi Pro", tokens: 50, price: 65000, note: "Cukup untuk revisi berulang naskah panjang.", featured: true },
  { id: "pkg_riset_intensif", name: "Riset Intensif", tokens: 150, price: 150000, note: "Untuk banyak naskah dan percakapan asisten." },
];

export const rupiah = (n: number) => `Rp ${n.toLocaleString("id-ID")}`;

export function useTokenPurchase() {
  const authStore = useAuthStore();
  const { showNotification } = useNotification();
  const invoices = ref<InvoiceRow[]>([]);
  const target = ref<PurchaseTarget | null>(null);
  const processing = ref(false);

  async function load() {
    void authStore.fetchProfile();
    try {
      const data = await billingService.listInvoices();
      invoices.value = (Array.isArray(data) ? data : []).map((i: any) => ({
        orderId: i.order_id || i.id || "-",
        name: i.package_name || "Top-up token",
        amount: Number(i.gross_amount) || 0,
        status: i.status || "PENDING",
        date: i.created_at ? new Date(i.created_at).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" }) : "-",
      }));
    } catch {
      invoices.value = [];
    }
  }

  async function confirm() {
    if (!target.value) return;
    processing.value = true;
    try {
      const res = await billingService.topup(target.value.id, target.value.tokenAmount);
      target.value = null;
      if (res.payment_ready && res.client_key) {
        const result = await openSnap(res.snap_token, res.client_key);
        const msg = result === "paid" ? "Pembayaran berhasil. Token segera masuk." : result === "pending" ? "Menunggu pembayaran Anda diselesaikan." : "Pembayaran belum diselesaikan.";
        showNotification(msg, result === "paid" ? "success" : "info");
      } else {
        showNotification(`Pesanan ${res.order_id} dicatat, tetapi pembayaran online belum diaktifkan.`, "info");
      }
      await Promise.all([load(), authStore.fetchProfile()]);
    } catch (err: any) {
      showNotification(err?.response?.data?.detail || "Pesanan belum bisa dibuat.", "error");
    } finally {
      processing.value = false;
    }
  }

  onMounted(load);
  return { invoices, target, processing, confirm };
}
