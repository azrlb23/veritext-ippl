export interface DemoSample {
  id: "T1" | "T2" | "T3";
  tierNumber: string;
  tierName: string;
  badgeLabel: string;
  colorHex: string;
  highlightBg: string;
  highlightBorder: string;
  originalText: string;
  highlightedSpan: string;
  postText: string;
  matchedSource: string;
  matchedAuthor: string;
  matchedSnippet: string;
  similarityScore: number;
  engineMetric: string;
  algorithmName: string;
  diagnosticNote: string;
}

export const demoSamples: DemoSample[] = [
  {
    id: "T1",
    tierNumber: "Tier 1",
    tierName: "Hashing Leksikal",
    badgeLabel: "Salin-Tempel Langsung",
    colorHex: "#EF4444",
    highlightBg: "bg-red-50 text-red-950",
    highlightBorder: "border-red-500",
    originalText: "Dalam pengujian ini terbukti bahwa ",
    highlightedSpan: "algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    postText: " Metode ini secara konsisten mempertahankan ketahanan terhadap transposisi kata.",
    matchedSource: "Dokumen Arsip IF-2023 #DOC-0941",
    matchedAuthor: "Repositori Dokumen Informatika",
    matchedSnippet: "algoritma Winnowing mereduksi jumlah fingerprint teks dengan memilih nilai hash minimum dalam jendela berukuran konstan.",
    similarityScore: 100,
    engineMetric: "k=5, w=4 (Hash Identik)",
    algorithmName: "Rabin-Karp Rolling Hash",
    diagnosticNote: "100% kecocokan n-gram leksikal terdeteksi tanpa perubahan token atau urutan kata.",
  },
  {
    id: "T2",
    tierNumber: "Tier 2",
    tierName: "Semantik Dense",
    badgeLabel: "Parafrasa Cerdas",
    colorHex: "#F97316",
    highlightBg: "bg-orange-50 text-orange-950",
    highlightBorder: "border-orange-500",
    originalText: "Eksperimen membuktikan bahwa ",
    highlightedSpan: "penerapan arsitektur jaringan saraf tiruan mampu meningkatkan efisiensi klasifikasi dokumen secara signifikan.",
    postText: " Hasil evaluasi menunjukkan konvergensi model yang lebih stabil.",
    matchedSource: "Jurnal Rekayasa Sistem Vol. 8 #CORP-2201",
    matchedAuthor: "Arsip Jurnal Nasional",
    matchedSnippet: "model deep learning terbukti mempercepat proses pengelompokan manuskrip riset dengan tingkat akurasi tinggi.",
    similarityScore: 89.4,
    engineMetric: "Jarak Kosinus d = 0.106",
    algorithmName: "pgvector HNSW (384 Dimensi)",
    diagnosticNote: "Struktur kalimat dan kosakata diubah dengan sinonim, tetapi vektor representasi 384D menempati ruang semantik berjarak sangat dekat.",
  },
  {
    id: "T3",
    tierNumber: "Tier 3",
    tierName: "Stilometri AI",
    badgeLabel: "Sintaksis Model LLM",
    colorHex: "#EAB308",
    highlightBg: "bg-amber-50 text-amber-950",
    highlightBorder: "border-amber-500",
    originalText: "Sebagai landasan berpikir, ",
    highlightedSpan: "penting untuk dicatat bahwa dalam era digital ini, integritas memainkan peranan yang sangat penting serta mendasar dalam menjaga kejujuran.",
    postText: " Hal ini menjadi pilar utama pembentukan karakter.",
    matchedSource: "Dataset Sintesis LLM Benchmark 2026",
    matchedAuthor: "Pola Sintaksis Generator AI",
    matchedSnippet: "Pola anomali: Kalimat transisi klise berulang dengan varians deviasi panjang kalimat mendekati nol (monoton).",
    similarityScore: 78.2,
    engineMetric: "Burstiness = 0.12, TTR = 0.38",
    algorithmName: "Varians Panjang & Type-Token Ratio",
    diagnosticNote: "Panjang kalimat sangat seragam dan distribusi leksikal rendah, mengindikasikan teks digenerasi otomatis oleh model bahasa AI.",
  },
];
