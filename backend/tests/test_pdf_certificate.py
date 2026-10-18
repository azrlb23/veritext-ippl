import unittest
import datetime
import pypdfium2
from app.services.pdf_certificate_service import generate_pdf_certificate, clean_pdf_filename


class TestPdfCertificateService(unittest.TestCase):
    def test_clean_pdf_filename(self):
        self.assertEqual(
            clean_pdf_filename("LPJ FPK.docx_compressed.pdf"),
            "Sertifikat_VeriText_LPJ_FPK_docx_compressed.pdf",
        )
        self.assertEqual(
            clean_pdf_filename("Tesis_Akhir.pdf"),
            "Sertifikat_VeriText_Tesis_Akhir.pdf",
        )
        self.assertEqual(
            clean_pdf_filename("   "),
            "Sertifikat_VeriText_Naskah_Akademik.pdf",
        )

    def test_generate_pdf_certificate_valid_pdf(self):
        pdf_bytes = generate_pdf_certificate(
            report_id="80b6be9c-21d0-4a0f-992c-3a10f21c9b30",
            verification_uuid="13c206aa-8c48-46c1-bfe7-05dad59b5a98",
            document_title="LPJ FPK.docx",
            user_name="Ibnu Dwiki Hermawan",
            institution="Universitas Airlangga",
            generated_at=datetime.datetime.now(),
            score_composite=35.31,
            score_lexical=47.37,
            score_semantic=0.00,
            score_stylometric=77.50,
            matched_sources=[
                {
                    "source_title": "Implementasi Sistem Deteksi Plagiarisme Cerdas",
                    "similarity": 0.4737,
                    "tier": "T1",
                }
            ],
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        # Verify with pypdfium2
        doc = pypdfium2.PdfDocument(pdf_bytes)
        self.assertEqual(len(doc), 1)
        text = doc[0].get_textpage().get_text_range()
        self.assertIn("VERITEXT AI", text)
        self.assertIn("LPJ FPK.docx", text)
        self.assertIn("Ibnu Dwiki Hermawan", text)
        self.assertIn("35.3%", text)


if __name__ == "__main__":
    unittest.main()
