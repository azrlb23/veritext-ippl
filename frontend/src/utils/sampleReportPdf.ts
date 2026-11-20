const BODY_LINES = [
  "Dokumen: Naskah-Laporan.pdf \\(2.140 kata, 1 token\\)",
  "Skor Orisinalitas: 88%",
  "Kecocokan kata: 8%",
  "Kecocokan makna: 14%",
  "Pola tulisan AI: 20%",
  "Status: Di bawah batas aman 20%",
];

function buildSamplePdf(): string {
  const stream = [
    "BT",
    "/F1 16 Tf 56 770 Td (VeriText AI - Laporan Sampel Orisinalitas) Tj",
    "/F1 11 Tf 0 -30 Td",
    ...BODY_LINES.map((line) => `(${line}) Tj 0 -22 Td`),
    "ET",
  ].join("\n");
  const objects = [
    "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
    "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
    `4 0 obj\n<< /Length ${stream.length} >>\nstream\n${stream}\nendstream\nendobj\n`,
    "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = objects.map((obj) => {
    const pos = pdf.length;
    pdf += obj;
    return `${String(pos).padStart(10, "0")} 00000 n \n`;
  });
  const xrefPos = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n${offsets.join("")}`;
  return `${pdf}trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefPos}\n%%EOF`;
}

export function downloadSampleReportPdf(): void {
  const url = URL.createObjectURL(new Blob([buildSamplePdf()], { type: "application/pdf" }));
  const link = Object.assign(document.createElement("a"), { href: url, download: "Laporan-Sampel-VeriText-AI.pdf" });
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
