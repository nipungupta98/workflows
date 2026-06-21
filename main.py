import os
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USERNAME = os.environ["SMTP_USERNAME"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]

today = datetime.now().strftime("%d %B %Y")

PROMPT_TEMPLATE = "=CRITICAL: Your entire response must be ONLY the HTML document. Begin with <!DOCTYPE html> as the first character. End with </html> as the last character. Do not write any explanation, search summary, or commentary. Do not use markdown code fences.\n\nThe date for today's briefing is: {today}. Use this EXACT string for the [[DATE]] placeholder. Do not generate or infer any other date.\n\nSearch the web for: (1) yesterday's closing values and 1-day % change for Nifty 50, Sensex, S&P 500, and USD/INR; (2) top 10 Indian finance and markets news from today; (3) top 10 world finance and markets news from today (US-focused); (4) top 10 general world news from today; (5) top 10 AI and technology news from today (covering AI model releases, AI company news, AI research breakthroughs, AI policy/regulation, and major tech industry moves). Then output the HTML template below EXACTLY, replacing only the [[PLACEHOLDERS]]. Do NOT change any HTML structure, table layout, inline styles, or styling. Output ONLY the completed HTML starting with <!DOCTYPE html> and ending with </html>. No preamble, no markdown code fences, no explanation before or after.\n\nFor each index card, if 1-day change is positive, use background:#dcfce7;color:#16a34a and arrow ▲. If negative, use background:#fee2e2;color:#dc2626 and arrow ▼.\n\nFor each news item: TITLE should be a short bold headline, SUMMARY should be 2-3 lines of context, SOURCE should be the publication name (e.g. Reuters, Bloomberg, Mint, FT, TechCrunch, The Verge), URL should be the real article link.\n\nTEMPLATE:\n\n<!DOCTYPE html><html><body style=\"margin:0;padding:0;background:#f4f6f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;\"><table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f4f6f8;padding:24px 12px;\"><tr><td align=\"center\"><table role=\"presentation\" width=\"640\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"max-width:640px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;\"><tr><td style=\"background:#0f172a;padding:28px 32px;\"><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tr><td><div style=\"font-size:11px;font-weight:600;color:#94a3b8;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;\">Morning Briefing</div><div style=\"font-size:24px;font-weight:700;color:#ffffff;\">[[DATE]]</div><div style=\"font-size:13px;color:#94a3b8;margin-top:4px;\">Markets, finance &amp; world news at a glance</div></td><td align=\"right\" valign=\"top\" style=\"font-size:28px;\">☀️</td></tr></table></td></tr><tr><td style=\"padding:24px 32px 8px;\"><div style=\"font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:14px;\">📊 Market Snapshot</div><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tr><td width=\"25%\" style=\"padding:0 4px;\"><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;\"><tr><td style=\"padding:14px 10px;text-align:center;\"><div style=\"font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;\">Nifty 50</div><div style=\"font-size:17px;font-weight:700;color:#0f172a;margin:6px 0 4px;\">[[NIFTY_VAL]]</div><div style=\"font-size:11px;font-weight:700;[[NIFTY_STYLE]];display:inline-block;padding:2px 8px;border-radius:20px;\">[[NIFTY_ARR]] [[NIFTY_CHG]]</div></td></tr></table></td><td width=\"25%\" style=\"padding:0 4px;\"><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;\"><tr><td style=\"padding:14px 10px;text-align:center;\"><div style=\"font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;\">Sensex</div><div style=\"font-size:17px;font-weight:700;color:#0f172a;margin:6px 0 4px;\">[[SENSEX_VAL]]</div><div style=\"font-size:11px;font-weight:700;[[SENSEX_STYLE]];display:inline-block;padding:2px 8px;border-radius:20px;\">[[SENSEX_ARR]] [[SENSEX_CHG]]</div></td></tr></table></td><td width=\"25%\" style=\"padding:0 4px;\"><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;\"><tr><td style=\"padding:14px 10px;text-align:center;\"><div style=\"font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;\">S&amp;P 500</div><div style=\"font-size:17px;font-weight:700;color:#0f172a;margin:6px 0 4px;\">[[SP500_VAL]]</div><div style=\"font-size:11px;font-weight:700;[[SP500_STYLE]];display:inline-block;padding:2px 8px;border-radius:20px;\">[[SP500_ARR]] [[SP500_CHG]]</div></td></tr></table></td><td width=\"25%\" style=\"padding:0 4px;\"><table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;\"><tr><td style=\"padding:14px 10px;text-align:center;\"><div style=\"font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;\">USD/INR</div><div style=\"font-size:17px;font-weight:700;color:#0f172a;margin:6px 0 4px;\">[[USDINR_VAL]]</div><div style=\"font-size:11px;font-weight:700;[[USDINR_STYLE]];display:inline-block;padding:2px 8px;border-radius:20px;\">[[USDINR_ARR]] [[USDINR_CHG]]</div></td></tr></table></td></tr></table></td></tr><tr><td style=\"padding:24px 32px 8px;\"><span style=\"display:inline-block;background:#fef3c7;color:#92400e;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;\">🇮🇳 India · Finance &amp; Markets</span></td></tr><tr><td style=\"padding:8px 32px 16px;\">[[INDIA_NEWS_ITEMS]]</td></tr><tr><td style=\"padding:16px 32px 8px;border-top:1px solid #f1f5f9;\"><span style=\"display:inline-block;background:#dbeafe;color:#1e40af;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;\">🌐 World · Finance &amp; Markets</span></td></tr><tr><td style=\"padding:8px 32px 16px;\">[[WORLD_FIN_ITEMS]]</td></tr><tr><td style=\"padding:16px 32px 8px;border-top:1px solid #f1f5f9;\"><span style=\"display:inline-block;background:#f3e8ff;color:#6b21a8;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;\">🌍 General World News</span></td></tr><tr><td style=\"padding:8px 32px 16px;\">[[GENERAL_NEWS_ITEMS]]</td></tr><tr><td style=\"padding:16px 32px 8px;border-top:1px solid #f1f5f9;\"><span style=\"display:inline-block;background:#ccfbf1;color:#0f766e;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;\">🤖 AI &amp; Technology</span></td></tr><tr><td style=\"padding:8px 32px 24px;\">[[AI_NEWS_ITEMS]]</td></tr><tr><td style=\"background:#f8fafc;padding:18px 32px;text-align:center;border-top:1px solid #e2e8f0;\"><div style=\"font-size:11px;color:#94a3b8;\">Curated by <span style=\"color:#0369a1;font-weight:600;\">Claude</span> · Delivered by <span style=\"color:#0369a1;font-weight:600;\">n8n</span></div><div style=\"font-size:10px;color:#cbd5e1;margin-top:4px;\">Have a productive day, Nipun ☕</div></td></tr></table></td></tr></table></body></html>\n\nFor each [[..._NEWS_ITEMS]] section, generate exactly 10 items using this exact format per item (with NN being item number 01-10):\n\n<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"margin-bottom:14px;border-top:1px solid #f1f5f9;padding-top:14px;\"><tr><td valign=\"top\" width=\"28\" style=\"padding-top:2px;\"><div style=\"font-size:11px;font-weight:700;color:#cbd5e1;\">NN</div></td><td valign=\"top\"><div style=\"font-size:14px;font-weight:700;color:#0f172a;line-height:1.4;margin-bottom:4px;\">TITLE</div><div style=\"font-size:13px;color:#475569;line-height:1.6;margin-bottom:6px;\">SUMMARY</div><a href=\"URL\" style=\"font-size:11px;color:#0369a1;font-weight:600;text-decoration:none;\">Read on SOURCE →</a></td></tr></table>"

prompt = PROMPT_TEMPLATE.format(today=today)

payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 24000,
    "tools": [
        {
            "type": "web_search_20250305",
            "name": "web_search"
        }
    ],
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
}

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    json=payload,
    timeout=300
)

response.raise_for_status()

data = response.json()

html_content = None

for block in reversed(data["content"]):
    if (
        block.get("type") == "text"
        and "<!DOCTYPE html>" in block.get("text", "")
    ):
        html_content = block["text"]
        break

if html_content is None:
    raise Exception("No HTML document found in Claude response")

with open("briefing.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Saved briefing.html")

msg = MIMEMultipart("alternative")
msg["Subject"] = f"Morning Briefing - {today}"
msg["From"] = EMAIL_FROM
msg["To"] = EMAIL_TO

msg.attach(MIMEText(html_content, "html"))

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.send_message(msg)

print("Email sent successfully.")
