from __future__ import annotations

import html
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(
    to_email: str,
    reset_url: str,
    user_name: str = "Pengguna VeriText",
    otp_code: str | None = None,
) -> bool:
    """Mengirim email pemulihan kata sandi melalui SMTP atau simulasi dev logging."""
    if settings.ENVIRONMENT.lower() != "production":
        otp_log = f"Kode OTP: {otp_code}\n" if otp_code else ""
        logger.info(f"[EMAIL DISPATCH] Pemulihan kata sandi untuk {to_email} (OTP: {otp_code or '-'}): {reset_url}")
        print(
            f"\n======================================================\n"
            f"[VERITEXT AI - TAUTAN RESET KATA SANDI]\n"
            f"Kepada: {to_email}\n"
            f"{otp_log}"
            f"Tautan: {reset_url}\n"
            f"(Berlaku selama 1 jam)\n"
            f"======================================================\n",
            flush=True,
        )
    else:
        logger.info("Dispatching password reset email to %s", to_email)

    if not settings.SMTP_HOST or not settings.SMTP_HOST.strip():
        logger.info("SMTP_HOST tidak dikonfigurasi. Tautan reset password tercatat di server log untuk keperluan pengembangan.")
        return False

    try:
        safe_name = html.escape(str(user_name or "Pengguna VeriText"))
        safe_url = html.escape(str(reset_url))
        safe_otp = html.escape(str(otp_code)) if otp_code else ""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "VeriText AI - Pemulihan Kata Sandi Akun"
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email

        otp_block = (
            f'<div style="background:#EBF8F6;border:1px solid #99F6E4;border-radius:12px;padding:16px;text-align:center;margin:16px 0;">'
            f'<div style="font-size:11px;font-weight:700;color:#0F766E;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Kode Verifikasi OTP</div>'
            f'<div style="font-size:28px;font-weight:800;letter-spacing:6px;color:#0B0F19;font-family:monospace;">{safe_otp}</div>'
            f'</div>'
            if safe_otp
            else ""
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #0B0F19; }}
            .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #E4E8F0; padding: 36px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #EBF8F6; color: #0F766E; border-radius: 100px; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 16px; }}
            h2 {{ font-size: 22px; font-weight: 800; margin: 0 0 12px 0; color: #0B0F19; }}
            p {{ font-size: 14px; line-height: 1.6; color: #5B6475; margin: 0 0 20px 0; }}
            .btn {{ display: inline-block; background: #0F766E; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 100px; font-size: 14px; font-weight: 600; margin: 8px 0 24px 0; }}
            .notice {{ font-size: 12px; color: #8B98AD; border-top: 1px solid #E4E8F0; padding-top: 16px; margin-top: 24px; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="badge">Keamanan Akun</div>
            <h2>Permintaan Reset Kata Sandi</h2>
            <p>Halo <strong>{safe_name}</strong>,</p>
            <p>Kami menerima permintaan untuk menyetel ulang kata sandi akun VeriText AI Anda. Gunakan kode OTP atau klik tombol di bawah ini untuk membuat kata sandi baru (berlaku selama 1 jam):</p>
            {otp_block}
            <div style="text-align: center;">
              <a href="{safe_url}" class="btn">Setel Ulang Kata Sandi Saya</a>
            </div>
            <p style="font-size: 12px; color: #5B6475;">Atau salin tautan berikut ke peramban web Anda:<br><a href="{safe_url}" style="color: #0F766E; word-break: break-all;">{safe_url}</a></p>
            <div class="notice">
              Jika Anda tidak merasa mengajukan permintaan ini, abaikan email ini. Kata sandi Anda akan tetap aman dan tidak berubah.
            </div>
          </div>
        </body>
        </html>
        """
        otp_text = f"Kode OTP Anda: {otp_code}\n\n" if otp_code else ""
        text_content = f"Halo {user_name},\n\n{otp_text}Permintaan reset kata sandi akun VeriText AI Anda dapat diproses melalui tautan berikut:\n{reset_url}\n\nTautan berlaku selama 1 jam.\nJika Anda tidak mengajukan ini, abaikan pesan ini."

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(msg)
        server.quit()
        logger.info(f"Email pemulihan kata sandi berhasil dikirim ke {to_email}")
        return True
    except Exception as exc:
        logger.warning(f"Gagal mengirim email reset kata sandi via SMTP ({type(exc).__name__}: {exc})")
        return False
