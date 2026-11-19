const SANDBOX_SNAP_SRC = "https://app.sandbox.midtrans.com/snap/snap.js";
const PRODUCTION_SNAP_SRC = "https://app.midtrans.com/snap/snap.js";

declare global {
  interface Window {
    snap?: { pay: (token: string, options: Record<string, () => void>) => void };
  }
}

function loadScript(clientKey: string, isProduction = false): Promise<void> {
  if (window.snap) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const tag = document.createElement("script");
    tag.src = isProduction ? PRODUCTION_SNAP_SRC : SANDBOX_SNAP_SRC;
    tag.dataset.clientKey = clientKey;
    tag.onload = () => resolve();
    tag.onerror = () => reject(new Error("Halaman pembayaran tidak dapat dimuat."));
    document.head.appendChild(tag);
  });
}

/** Membuka jendela pembayaran Midtrans Snap; mengembalikan hasil akhir yang dipilih pengguna. */
export async function openSnap(token: string, clientKey: string, isProduction = false): Promise<"paid" | "pending" | "closed"> {
  await loadScript(clientKey, isProduction);
  return new Promise((resolve) => {
    window.snap!.pay(token, {
      onSuccess: () => resolve("paid"),
      onPending: () => resolve("pending"),
      onError: () => resolve("closed"),
      onClose: () => resolve("closed"),
    });
  });
}
