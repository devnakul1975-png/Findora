"""
SmartCampus MITS (Lost & Found) - Email Notification Service
Handles automated welcome emails upon user registration, ownership claim verifications,
and status updates via Gmail SMTP or API service.
"""

import os
import ssl
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
import urllib.request
import json

logger = logging.getLogger("smartcampus.email")

# Config from environment
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER") or os.environ.get("GMAIL_USER") or ""
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") or os.environ.get("SMTP_PASS") or os.environ.get("GMAIL_APP_PASSWORD") or ""
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "SmartCampus Lost & Found - MITS")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

def generate_welcome_html(user_name: str, to_email: str, role: str = "student") -> str:
    role_label = "Faculty Member" if role.lower() == "faculty" else "Institute Student"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to SmartCampus Lost &amp; Found (MITS Gwalior)</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #0b0f19;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 20px auto;
      background: #111827;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }}
    .header {{
      background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
      padding: 32px 24px;
      text-align: center;
      border-bottom: 1px solid rgba(59, 130, 246, 0.3);
    }}
    .brand-mark {{
      display: inline-block;
      width: 44px;
      height: 44px;
      line-height: 44px;
      border-radius: 10px;
      background: #2563eb;
      color: #ffffff;
      font-size: 24px;
      font-weight: 800;
      margin-bottom: 10px;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      color: #ffffff;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .header p {{
      margin: 6px 0 0;
      color: #93c5fd;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .content {{
      padding: 30px 24px;
    }}
    .greeting {{
      font-size: 18px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 14px;
    }}
    .lead {{
      font-size: 15px;
      line-height: 1.6;
      color: #cbd5e1;
      margin-bottom: 24px;
    }}
    .card {{
      background: #1f2937;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 24px;
    }}
    .card-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 13.5px;
    }}
    .card-row:last-child {{
      border-bottom: none;
    }}
    .card-label {{
      color: #94a3b8;
    }}
    .card-val {{
      color: #f1f5f9;
      font-weight: 600;
    }}
    .btn-container {{
      text-align: center;
      margin: 28px 0;
    }}
    .btn {{
      display: inline-block;
      background: #2563eb;
      color: #ffffff !important;
      text-decoration: none;
      padding: 13px 28px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 15px;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
    }}
    .feature-list {{
      background: rgba(30, 41, 59, 0.6);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 24px;
    }}
    .feature-item {{
      margin-bottom: 12px;
      font-size: 13.5px;
      line-height: 1.5;
      color: #cbd5e1;
    }}
    .feature-item:last-child {{
      margin-bottom: 0;
    }}
    .footer {{
      background: #0f172a;
      padding: 24px;
      text-align: center;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 12px;
      color: #64748b;
      line-height: 1.5;
    }}
    .footer a {{
      color: #60a5fa;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div class="brand-mark">✓</div>
      <h1>SmartCampus MITS</h1>
      <p>Findora Lost & Found Network</p>
    </div>

    <div class="content">
      <div class="greeting">Welcome, {user_name}! 👋</div>
      <p class="lead">
        Your institute account has been verified and registered on the <strong>SmartCampus Findora</strong> network at Madhav Institute of Technology & Science (MITS Gwalior).
      </p>

      <div class="card">
        <div class="card-row">
          <span class="card-label">Registered Name:</span>
          <span class="card-val">{user_name}</span>
        </div>
        <div class="card-row">
          <span class="card-label">Email Address:</span>
          <span class="card-val">{to_email}</span>
        </div>
        <div class="card-row">
          <span class="card-label">Account Role:</span>
          <span class="card-val">{role_label}</span>
        </div>
        <div class="card-row">
          <span class="card-label">Campus Center:</span>
          <span class="card-val">MITS Gwalior (Central Hub)</span>
        </div>
        <div class="card-row">
          <span class="card-label">Account Status:</span>
          <span class="card-val" style="color: #10b981;">● Active & Ready</span>
        </div>
      </div>

      <div class="btn-container">
        <a href="https://smartcampusmits.vercel.app/" class="btn" target="_blank">
          Open SmartCampus Portal →
        </a>
      </div>

      <div class="feature-list">
        <strong style="color: #93c5fd; display: block; margin-bottom: 8px; font-size: 14px;">How to use Findora on Campus:</strong>
        <div class="feature-item">
          📍 <strong>Report Lost Belongings</strong> — Pinpoint the exact room, hall, or lab (e.g. CIoT Lab M007, Canteen, Central Library) to trigger instant AI alerts.
        </div>
        <div class="feature-item">
          🛡️ <strong>1-Step Ownership Verification</strong> — Found items are securely logged. Submit your private identifying mark (e.g. lock screen wallpaper, engraved mark) to authorize pickup at the Central Library Circulation Desk.
        </div>
        <div class="feature-item">
          🤖 <strong>AI Semantic Matchmaker</strong> — Automatically matches lost items with recently found submissions across campus departments.
        </div>
      </div>

      <p style="font-size: 13px; color: #94a3b8; text-align: center; margin: 0;">
        Need to hand over a found item? You can deposit it with the Security Desk at the Main Gate or the Central Library Reception.
      </p>
    </div>

    <div class="footer">
      <p>
        <strong>SmartCampus MITS Gwalior</strong><br>
        Madhav Institute of Technology & Science, Gola Ka Mandir, Gwalior, MP 474005<br>
        Web: <a href="https://smartcampusmits.vercel.app/" target="_blank">smartcampusmits.vercel.app</a>
      </p>
      <p style="margin-top: 10px; font-size: 11px;">
        This automated confirmation was dispatched because an account was registered with {to_email}. If you did not create this account, please notify security@mitsgwalior.in.
      </p>
    </div>
  </div>
</body>
</html>"""

def _get_email_config() -> Dict[str, Any]:
    """Read email credentials dynamically from environment at send time."""
    raw_pass = os.environ.get("SMTP_PASSWORD") or os.environ.get("SMTP_PASS") or os.environ.get("GMAIL_APP_PASSWORD") or ""
    # Strip spaces automatically in case user pastes Google's 16-char 'xxxx xxxx xxxx xxxx' App Password directly
    clean_pass = raw_pass.replace(" ", "").strip()
    return {
        "smtp_host": os.environ.get("SMTP_HOST", "smtp.gmail.com").strip(),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "smtp_user": (os.environ.get("SMTP_USER") or os.environ.get("GMAIL_USER") or "").strip(),
        "smtp_pass": clean_pass,
        "from_name": os.environ.get("SMTP_FROM_NAME", "Smart Campus Lost & Found - MITS").strip(),
        "resend_key": os.environ.get("RESEND_API_KEY", "").strip(),
        "resend_from": os.environ.get("RESEND_FROM", "SmartCampus MITS <onboarding@resend.dev>").strip(),
    }


def _dispatch_email(to_email: str, subject: str, text_content: str, html_content: str) -> Dict[str, Any]:
    """Shared email transport via Resend HTTP API or Gmail/TLS/SSL SMTP, with simulated demo fallback."""
    cfg = _get_email_config()

    # Option 1: Gmail SMTP / Standard SMTP (works to any student Gmail inbox with 16-char App Password)
    if cfg["smtp_user"] and cfg["smtp_pass"]:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{cfg['from_name']} <{cfg['smtp_user']}>"
            msg["To"] = to_email
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            context = ssl.create_default_context()
            if cfg["smtp_port"] == 465:
                with smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], timeout=12, context=context) as server:
                    server.login(cfg["smtp_user"], cfg["smtp_pass"])
                    server.sendmail(cfg["smtp_user"], [to_email], msg.as_string())
            else:
                with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=12) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(cfg["smtp_user"], cfg["smtp_pass"])
                    server.sendmail(cfg["smtp_user"], [to_email], msg.as_string())

            logger.info(f"Email successfully sent via SMTP to {to_email}")
            return {"sent": True, "simulated": False, "provider": "smtp", "to": to_email}
        except Exception as e:
            logger.error(f"SMTP dispatch error to {to_email}: {e}")
            smtp_err = str(e)
            # Fall through to Resend API if configured, otherwise return clean SMTP failure info
            if not cfg["resend_key"]:
                return {
                    "sent": False,
                    "simulated": True,
                    "provider": "smtp",
                    "error": smtp_err,
                    "message": f"SMTP send failed ({smtp_err}). Verify Gmail App Password & SMTP_USER."
                }

    # Option 2: Resend HTTP API fallback / primary
    if cfg["resend_key"]:
        try:
            req_data = {
                "from": cfg["resend_from"],
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {cfg['resend_key']}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Email sent via Resend API to {to_email}")
                    return {"sent": True, "simulated": False, "provider": "resend", "to": to_email}
        except Exception as e:
            logger.warning(f"Resend API send failed: {e}")
            return {
                "sent": False,
                "simulated": True,
                "provider": "resend",
                "error": str(e),
                "message": f"Resend API failed: {str(e)}"
            }

    # Fallback / Simulated mode when no mail provider env vars are configured
    logger.info(f"[DEMO / SIMULATED] Email prepared for {to_email}. Add SMTP_USER & SMTP_PASSWORD to send live.")
    return {
        "sent": False,
        "simulated": True,
        "to": to_email,
        "message": "Email simulated (configure SMTP_USER & SMTP_PASSWORD in Vercel env vars for live Gmail delivery)."
    }


def send_welcome_email(to_email: str, user_name: str, role: str = "student") -> Dict[str, Any]:
    """Sends a welcome confirmation email to the user's Gmail / institute address."""
    if not to_email or "@" not in to_email:
        return {"sent": False, "simulated": True, "reason": "Invalid email address"}

    html_content = generate_welcome_html(user_name, to_email, role)
    text_content = (
        f"Welcome to Smart Campus Lost & Found (MITS Gwalior), {user_name}!\n\n"
        f"Your account ({to_email}) has been registered.\n"
        f"Visit https://smartcampusmits.vercel.app/ to report or claim lost items.\n\n"
        f"Campus Desk: Central Library Circulation Desk\n"
        f"Madhav Institute of Technology & Science, Gwalior"
    )
    subject = "Welcome to Smart Campus Lost & Found (MITS Gwalior)"
    return _dispatch_email(to_email, subject, text_content, html_content)


def send_password_reset_otp_email(to_email: str, otp: str, user_name: str = "Student") -> Dict[str, Any]:
    """Sends a 6-digit OTP security code to the user's private email address."""
    if not to_email or "@" not in to_email:
        return {"sent": False, "simulated": True, "reason": "Invalid email address"}

    subject = f"Your SmartCampus Password Reset Code: {otp}"
    text_content = (
        f"Hello {user_name},\n\n"
        f"A password reset was requested for your Smart Campus Lost & Found (MITS) account.\n\n"
        f"Your 6-Digit Verification Code is:\n"
        f"  {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you did not request this code, ignore this message.\n\n"
        f"Madhav Institute of Technology & Science, Gwalior"
    )
    html_content = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:24px;background:#0b0f19;font-family:-apple-system,sans-serif;color:#e2e8f0;">
  <div style="max-width:520px;margin:0 auto;background:#111827;border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:32px;text-align:center;">
    <div style="font-size:28px;margin-bottom:12px;">🔒</div>
    <h2 style="color:#ffffff;margin:0 0 8px;">Password Reset Verification</h2>
    <p style="color:#94a3b8;font-size:14px;margin:0 0 24px;">Use the one-time security code below to reset your password on Smart Campus Lost &amp; Found.</p>
    <div style="background:rgba(59,130,246,0.15);border:2px dashed #3b82f6;border-radius:10px;padding:16px 24px;display:inline-block;margin-bottom:24px;">
      <span style="font-family:monospace;font-size:32px;font-weight:900;letter-spacing:6px;color:#60a5fa;">{otp}</span>
    </div>
    <p style="color:#64748b;font-size:12px;margin:0;">Valid for 10 minutes. If you did not make this request, please ignore this email.</p>
  </div>
</body>
</html>"""

    res = _dispatch_email(to_email, subject, text_content, html_content)
    if res.get("simulated"):
        res["otp"] = otp
    return res
