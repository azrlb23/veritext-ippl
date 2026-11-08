import os
import sys
import shutil

BASE_DIR = "/Users/azrlb23/Documents/IPPL/diagrams"
DRAWIO_DIR = os.path.join(BASE_DIR, "drawio")
EXPORT_DIR = os.path.join(BASE_DIR, "exported")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

EXPECTED_29_DIAGRAMS = [
    # 7 Structural & Architectural Diagrams
    "Use Case Diagram",
    "Architecture Diagram",
    "Component Diagram",
    "Class Diagram",
    "DFD0-Context Diagram",
    "DFD1-System Overview",
    "DFD2-Deteksi Plagiarisme Hybrid dan AI Chatbot",
    # 11 Activity Diagrams
    "AD1-Masuk dan Registrasi Akun",
    "AD2-Kelola Profil dan Kata Sandi",
    "AD3-Unggah dan Validasi Naskah",
    "AD4-Deteksi Plagiarisme Hybrid 3-Tahap",
    "AD5-Tinjau Laporan dan Heatmap Kemiripan",
    "AD6-Konsultasi Naskah via AI Chatbot",
    "AD7-Parafrase Instan dan Cek Ulang Kalimat",
    "AD8-Unduh Laporan PDF dan Verifikasi QR",
    "AD9-Kelola dan Hapus Riwayat Naskah",
    "AD10-Beli Kuota Token dan Upgrade Premium",
    "AD11-Pantau Dasbor Analitik dan Log Transaksi",
    # 11 Sequence Diagrams
    "SD1-Masuk dan Registrasi Akun",
    "SD2-Kelola Profil dan Kata Sandi",
    "SD3-Unggah dan Validasi Naskah",
    "SD4-Deteksi Plagiarisme Hybrid 3-Tahap",
    "SD5-Tinjau Laporan dan Heatmap Kemiripan",
    "SD6-Konsultasi Naskah via AI Chatbot",
    "SD7-Parafrase Instan dan Cek Ulang Kalimat",
    "SD8-Unduh Laporan PDF dan Verifikasi QR",
    "SD9-Kelola dan Hapus Riwayat Naskah",
    "SD10-Beli Kuota Token dan Upgrade Premium",
    "SD11-Pantau Dasbor Analitik dan Log Transaksi"
]

def clean_obsolete_files():
    print("--- 1. Cleaning Obsolete Files ---")
    obsolete_patterns = ["AD12", "SD12", "DFD2-P5", "AD-12", "UC-12", "UC-09_Order_Payment_Activity_Map"]
    for folder in [DRAWIO_DIR, EXPORT_DIR]:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            for pat in obsolete_patterns:
                if pat in fname:
                    fpath = os.path.join(folder, fname)
                    print(f"Removing obsolete file: {fpath}")
                    os.remove(fpath)

def run_generators():
    print("\n--- 2. Executing Diagram Generators ---")
    sys.path.insert(0, SCRIPTS_DIR)
    
    import generate_structural_drawio
    generate_structural_drawio.main()

    import generate_ad_drawio
    generate_ad_drawio.main()

    import generate_sd_drawio
    generate_sd_drawio.main()

def verify_all_diagrams():
    print("\n--- 3. Verifying Exact 29 Diagrams ---")
    drawio_missing = []
    png_missing = []

    for name in EXPECTED_29_DIAGRAMS:
        drawio_path = os.path.join(DRAWIO_DIR, f"{name}.drawio")
        png_path = os.path.join(EXPORT_DIR, f"{name}.png")

        if not os.path.exists(drawio_path) or os.path.getsize(drawio_path) == 0:
            drawio_missing.append(name)
        if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
            png_missing.append(name)

    if drawio_missing:
        print(f"FAILED: Missing .drawio files ({len(drawio_missing)}): {drawio_missing}")
    else:
        print(f"SUCCESS: All 29 .drawio files exist with non-zero size in {DRAWIO_DIR}")

    if png_missing:
        print(f"FAILED: Missing .png files ({len(png_missing)}): {png_missing}")
    else:
        print(f"SUCCESS: All 29 .png files exist with non-zero size in {EXPORT_DIR}")

    # Also copy to docs/activity_diagrams/png/ and docs/diagrams for markdown preview accessibility if needed
    dest_dir = "/Users/azrlb23/Documents/IPPL/docs/activity_diagrams/png"
    os.makedirs(dest_dir, exist_ok=True)
    for name in EXPECTED_29_DIAGRAMS:
        src_png = os.path.join(EXPORT_DIR, f"{name}.png")
        dst_png = os.path.join(dest_dir, f"{name}.png")
        shutil.copy2(src_png, dst_png)
    print(f"Synchronized 29 PNGs to {dest_dir}")

    total_drawio = len([f for f in os.listdir(DRAWIO_DIR) if f.endswith('.drawio')])
    total_png = len([f for f in os.listdir(EXPORT_DIR) if f.endswith('.png')])
    print(f"\nFinal Summary: {total_drawio} .drawio files, {total_png} .png files.")
    assert len(EXPECTED_29_DIAGRAMS) == 29
    assert len(drawio_missing) == 0
    assert len(png_missing) == 0

def main():
    clean_obsolete_files()
    run_generators()
    verify_all_diagrams()

if __name__ == "__main__":
    main()
