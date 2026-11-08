const FIELD_LABELS: Record<string, string> = {
  email: "alamat email",
  password: "kata sandi",
  full_name: "nama lengkap",
  new_password: "kata sandi baru",
};

/** Mengubah detail galat API (teks atau daftar galat validasi) menjadi kalimat yang mudah dibaca. */
export function readableDetail(detail: unknown, fallback: string): string {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length) {
    const fields = detail
      .map((d: any) => FIELD_LABELS[String(d?.field ?? d?.loc?.slice?.(-1)?.[0] ?? "")] || null)
      .filter((f, i, all): f is string => !!f && all.indexOf(f) === i);
    return fields.length ? `Periksa kembali ${fields.join(" dan ")} Anda.` : fallback;
  }
  return fallback;
}
