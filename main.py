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

PROMPT_TEMPLATE = """
CRITICAL: Your entire response must be ONLY the HTML document.
Begin with <!DOCTYPE html>.
End with </html>.

The date for today's briefing is: {today}.

PASTE YOUR EXISTING PROMPT HERE
AND REPLACE:

{{ $('Edit Fields').item.json.today }}

WITH:

{today}
"""

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

html_content = ""

for block in data["content"]:
if block["type"] == "text":
html_content += block["text"]

if "<!DOCTYPE html>" not in html_content:
raise Exception("Claude did not return HTML")

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
